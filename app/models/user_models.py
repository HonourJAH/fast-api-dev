from sqlmodel import SQLModel
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field


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
