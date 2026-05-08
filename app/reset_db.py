# reset_db.py
from sqlmodel import SQLModel
from app.database import engine
from app.schemas import post_schema, user_schema

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
print("Tables recreated successfully")
