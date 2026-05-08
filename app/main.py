from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import post_routes, user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(post_routes.router)
app.include_router(user_routes.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to my fastapi development page"}
