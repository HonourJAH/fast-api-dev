from sqlmodel import SQLModel
from datetime import datetime


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
