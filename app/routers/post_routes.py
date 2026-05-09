from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models.post_models import (
    Post,
    PostCreate,
    PostPublic,
    PostUpdate,
    PostsWithOwnerResponse,
)

from app.models.user_models import UserInDB
from app.routers.authentication import get_current_user

router = APIRouter(tags=["Posts"])


# CREATE POST
@router.post("/post", status_code=status.HTTP_201_CREATED, response_model=PostPublic)
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


# GET POST
@router.get("/posts/{post_id}", response_model=PostPublic)
def get_post(
    post_id: int,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    # post = session.get(Post, post_id)
    post = session.exec(
        select(Post).where(Post.id == post_id, Post.user_id == current_user.id)
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


# GET ALL POSTS
@router.get("/posts", response_model=PostsWithOwnerResponse)
def get_all_posts(
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = None,
):
    query = select(Post)

    if search:
        query = query.where(Post.title.contains(search))

    posts = session.exec(query.limit(limit).offset(skip)).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No posts found"
        )
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
