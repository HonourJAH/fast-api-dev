from fastapi import status


def get_auth_token(client):
    # create a user and login to get token
    client.post("/users", json={"email": "test@gmail.com", "password": "password123"})
    response = client.post(
        "/login", data={"username": "test@gmail.com", "password": "password123"}
    )
    return response.json()["access_token"]


def test_create_post(client):
    token = get_auth_token(client)
    response = client.post(
        "/posts",
        json={"title": "Test Post", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content"


def test_get_all_posts(client):
    token = get_auth_token(client)

    # create a post to ensure there's at least one post in the database
    client.post(
        "/posts",
        json={"title": "Test Post", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get("/posts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK


def test_get_post_not_found(client):
    token = get_auth_token(client)
    response = client.get("/posts/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
