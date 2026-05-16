# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user_models import User
from app.models.post_models import Post
from app.models.vote_models import Vote

# use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(
    name="session"
)  # fixture to create a new database session for each test
def session_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # keeps the same connection for the entire test
    )
    SQLModel.metadata.create_all(engine)  # create all tables

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)  # drop all tables after test


@pytest.fixture(
    name="client"
)  # fixture to create a TestClient that uses the test database session
def client_fixture(session: Session):
    def get_session_override():
        yield session

    # override the real database session with the test session
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()  # clear overrides after test
