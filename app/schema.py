from sqlmodel import DateTime, Field
from datetime import datetime
from sqlalchemy import Column, text

from app.model import PostBase, UserBase


class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),  # ← wrap in text()
            nullable=False,
        )
    )


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),  # ← wrap in text()
            nullable=False,
        )
    )
