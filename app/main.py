from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import select
from contextlib import asynccontextmanager
from app.database import create_db_and_tables, SessionDep

from app.model import (
    PostCreate,
    PostPublic,
    PostUpdate,
    PostsResponse,
    CreateUser,
    UserPublic,
    UsersResponse,
    UserUpdate,
)
from app.schema import Post, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to my fastapi developement page"}


# POST ROUTE OPERATIONS
# create a post
@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, session: SessionDep):
    post = Post(**post.model_dump())
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


# get a post by id
@app.get("/post/{post_id}", response_model=PostPublic)
def get_post(post_id: int, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


# # get all posts
@app.get("/posts", response_model=PostsResponse)
def get_all_posts(session: SessionDep):
    posts = session.exec(select(Post)).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No posts found"
        )

    return PostsResponse(results=len(posts), data=posts)


# update a post using the patch method
@app.patch("/posts/{post_id}", response_model=PostPublic)
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


# delete a post
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, session: SessionDep):
    post_db = session.get(Post, post_id)
    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    session.delete(post_db)
    session.commit()
    return None


# ---------------------------------------------------------------------------------------------------


# USER ROUTE OPERATIONS
# create a user
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def create_user(user: CreateUser, session: SessionDep):
    user = User(**user.model_dump())

    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There's already a user with that email. Please choose another email",
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# get a user by id
@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# get all users
@app.get("/users", response_model=UsersResponse)
def get_all_users(session: SessionDep):
    users = session.exec(select(User)).all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    return UsersResponse(results=len(users), data=users)


# delete a user
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user_db)
    session.commit()
    return None


# update a user using the patch method
@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_data = user.model_dump(exclude_unset=True)

    if "email" in user_data:
        if session.exec(select(User).where(User.email == user_data["email"])).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There's already a user with that email. Please choose another email",
            )

    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


# --------

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# OAUTH_SCHEME = Annotated[str, Depends(oauth2_scheme)]


# @app.get("/items/")
# async def read_items(token: OAUTH_SCHEME):
#     return {"token": token}
