from sqlmodel import Relationship, SQLModel, DateTime, Field
from datetime import datetime
from sqlalchemy import Column, text
from app.models.user_models import User, UserPublic


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = True
    rating: float | None = None


class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),  # ← wrap in text()
            nullable=False,
        )
    )
    user_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="posts")


class PostPublic(PostBase):
    created_at: datetime
    user_id: int
    votes: int = 0
    id: int


class PostWithOwner(PostPublic):
    owner: UserPublic


class PostsWithOwnerResponse(SQLModel):
    results: int
    data: list[PostWithOwner]


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
