from datetime import datetime, timezone
from pydantic import EmailStr
from sqlmodel import Relationship, SQLModel, DateTime, Field
from sqlalchemy import Column, text

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.post_models import Post


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)
    password: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # created_at: datetime = Field(
    #     sa_column=Column(
    #         DateTime(timezone=True),
    #         default_factory=lambda: datetime.now(timezone.utc),
    #         nullable=False,
    #     )
    # )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    posts: list["Post"] = Relationship(back_populates="owner")


class UserPublicAll(SQLModel):
    id: int
    created_at: datetime
    email: EmailStr


class UserPublic(SQLModel):
    email: EmailStr


class CreateUser(UserBase):
    pass


class UserUpdate(UserBase):
    email: EmailStr | None = None
    password: str | None = None


class UsersResponse(SQLModel):
    results: int
    data: list[UserPublicAll]


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: EmailStr | None = None


class UserInDB(UserBase):
    id: int
