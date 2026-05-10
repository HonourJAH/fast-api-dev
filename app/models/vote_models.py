from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, DateTime, text


class Vote(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    post_id: int = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            nullable=False,
        )
    )
