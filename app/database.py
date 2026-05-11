from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.models.user_models import User
from app.models.post_models import Post

from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    # SQLModel.metadata.create_all(engine)
    pass


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
