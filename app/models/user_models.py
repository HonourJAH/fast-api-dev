from datetime import datetime
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
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            nullable=False,
        )
    )
    posts: list["Post"] = Relationship(back_populates="owner")


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
    hashed_password: str
