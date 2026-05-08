from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models.post_models import PostCreate, PostPublic, PostUpdate, PostsResponse
from app.schemas.post_schema import Post

router = APIRouter(tags=["Posts"])


@router.post("/post", status_code=status.HTTP_201_CREATED, response_model=PostPublic)
def create_post(post: PostCreate, session: SessionDep):
    post = Post(**post.model_dump())
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.get("/posts/{post_id}", response_model=PostPublic)
def get_post(post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get("/posts", response_model=PostsResponse)
def get_all_posts(session: SessionDep):
    posts = session.exec(select(Post)).all()
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No posts found"
        )
    return PostsResponse(results=len(posts), data=posts)


@router.patch("/posts/{post_id}", response_model=PostPublic)
def update_post(post_id: int, post: PostUpdate, session: SessionDep):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    post_data = post.model_dump(exclude_unset=True)
    post_db.sqlmodel_update(post_data)
    session.add(post_db)
    session.commit()
    session.refresh(post_db)
    return post_db


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, session: SessionDep):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    session.delete(post_db)
    session.commit()
    return None
