from sqlmodel import SQLModel
from app.database import engine
from app.models.user_models import User
from app.models.post_models import Post

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)
print("Tables recreated successfully")
