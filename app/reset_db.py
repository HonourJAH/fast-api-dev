# reset_db.py
from sqlmodel import SQLModel
from app.database import engine
from app.schema import Post, User

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
print("Tables recreated successfully")
