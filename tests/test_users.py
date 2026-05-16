import pytest

from app.models import user_models
from fastapi import status


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to my fastapi development page"}


def test_create_user(client):
    response = client.post(
        "/users", json={"email": "test@gmail.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@gmail.com"
    assert "id" in data


def test_create_user_duplicate_email(client):
    # create first user
    client.post("/users", json={"email": "test@gmail.com", "password": "password123"})

    # try creating with same email
    response = client.post(
        "/users", json={"email": "test@gmail.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_get_user(client):
    # create a user first
    create_response = client.post(
        "/users", json={"email": "test@gmail.com", "password": "password123"}
    )
    user_id = create_response.json()["id"]

    # get the user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@gmail.com"


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_users(client):
    # create a user first
    client.post("/users", json={"email": "test@gmail.com", "password": "password123"})

    # get all users
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["email"] == "test@gmail.com"


def test_delete_user(client):
    # create a user
    create_response = client.post(
        "/users", json={"email": "test@gmail.com", "password": "password123"}
    )
    user_id = create_response.json()["id"]

    # login to get token
    login_response = client.post(
        "/login", data={"username": "test@gmail.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # delete with token in header
    response = client.delete(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"}  # ← add this
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # try getting the deleted user
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_login_user(client):
    # create a user first
    client.post("/users", json={"email": "test@gmail.com", "password": "password123"})

    # try to login
    response = client.post(
        "/login", data={"username": "test@gmail.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("test@gmail.com", "wrongpassword", 401),
        ("invalidemail", "password123", 401),
        ("invalidemail", "wrongpassword", 401),
    ],
)
def test_login_user_invalid_credentials(client, email, password, status_code):
    # create a user first
    client.post("/users", json={"email": "test@gmail.com", "password": "password123"})

    # try to login with invalid credentials
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status_code
    assert response.json()["detail"] == "Invalid email or password"
