from sqlmodel import DateTime, SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, text
from pydantic import EmailStr


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = True
    rating: float | None = None


class PostPublic(PostBase):
    id: int
    created_at: datetime


class PostsResponse(SQLModel):
    results: int
    data: list[PostPublic]


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
    rating: float | None = None


# USER SCHEMAS -----------------------------------------------------------------------


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)
    password: str


class UserPublic(SQLModel):
    id: int
    created_at: datetime
    email: EmailStr


class CreateUser(UserBase):
    pass


class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None


class UsersResponse(SQLModel):
    results: int
    data: list[UserPublic]
