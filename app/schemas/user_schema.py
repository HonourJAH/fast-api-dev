from sqlmodel import DateTime, Field
from datetime import datetime
from sqlalchemy import Column, text

from app.models.user_models import UserBase


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            nullable=False,
        )
    )
