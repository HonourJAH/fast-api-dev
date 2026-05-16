from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, func
from app.models.user_models import User, UserPublic

from app.database import SessionDep
from app.models.post_models import (
    Post,
    PostCreate,
    PostPublic,
    PostUpdate,
    PostWithOwner,
    PostsWithOwnerResponse,
)

from app.models.user_models import UserInDB
from app.routers.authentication import get_current_user

from app.models.vote_models import Vote

router = APIRouter(tags=["Posts"])


# CREATE POST
@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=PostPublic)
def create_post(
    post: PostCreate,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    post = Post(**post.model_dump(), user_id=current_user.id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


# GET SINGLE POST
@router.get("/posts/{post_id}", response_model=PostPublic)
def get_post(post_id: int, session: SessionDep):

    result = session.exec(
        select(Post, func.count(Vote.post_id).label("votes"))
        .outerjoin(Vote, Vote.post_id == Post.id)
        .where(Post.id == post_id)
        .group_by(Post.id)
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post, vote_count = result
    return PostPublic(**post.model_dump(), votes=vote_count)


# # GET ALL POSTS
@router.get("/posts", response_model=PostsWithOwnerResponse)
def get_all_posts(
    session: SessionDep,
    # current_user: UserInDB = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = None,
):
    query = (
        select(Post, User, func.count(Vote.post_id).label("votes"))
        .join(User, User.id == Post.user_id)
        .outerjoin(Vote, Vote.post_id == Post.id)
        .group_by(Post.id, User.id)
    )

    if search:
        query = query.where(Post.title.contains(search))

    results = session.exec(query.limit(limit).offset(skip)).all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No posts found"
        )

    posts = [
        PostWithOwner(
            **post.model_dump(),
            votes=vote_count,
            owner=UserPublic.model_validate(user.model_dump())
        )
        for post, user, vote_count in results
    ]

    return PostsWithOwnerResponse(results=len(posts), data=posts)


# UPDATE POST
@router.patch("/posts/{post_id}", response_model=PostPublic)
def update_post(
    post_id: int,
    post: PostUpdate,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    post_data = post.model_dump(exclude_unset=True)

    if post_db.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )
    post_db.sqlmodel_update(post_data)
    session.add(post_db)
    session.commit()
    session.refresh(post_db)
    return post_db


# DELETE POST
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post_db.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    session.delete(post_db)
    session.commit()
    return None
