from fastapi import status


def create_user_and_login(client, email="test@gmail.com", password="password123"):
    """helper function to create a user and return their token"""
    client.post("/users", json={"email": email, "password": password})
    response = client.post("/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def create_post(client, token):
    """helper function to create a post and return its id"""
    response = client.post(
        "/posts",
        json={"title": "Test Post", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


# VOTE TESTS
def test_vote_on_post(client):
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    response = client.post(
        f"/vote/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Vote added successfully"


def test_vote_twice_removes_vote(client):
    """voting on a post you already voted on should remove the vote"""
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    # vote first time
    client.post(f"/vote/{post_id}", headers={"Authorization": f"Bearer {token}"})

    # vote second time - should remove vote
    response = client.post(
        f"/vote/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Vote removed successfully"


def test_vote_on_nonexistent_post(client):
    token = create_user_and_login(client)

    response = client.post("/vote/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_vote_without_authentication(client):
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    # try to vote without token
    response = client.post(f"/vote/{post_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_vote_count_increases(client):
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    # get post before voting
    before = client.get(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    votes_before = before.json()["votes"]

    # vote on the post
    client.post(f"/vote/{post_id}", headers={"Authorization": f"Bearer {token}"})

    # get post after voting
    after = client.get(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    votes_after = after.json()["votes"]

    assert votes_after == votes_before + 1


def test_vote_count_decreases_after_unvote(client):
    token = create_user_and_login(client)
    post_id = create_post(client, token)

    # vote first
    client.post(f"/vote/{post_id}", headers={"Authorization": f"Bearer {token}"})

    # unvote
    client.post(f"/vote/{post_id}", headers={"Authorization": f"Bearer {token}"})

    # get post after unvoting
    response = client.get(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.json()["votes"] == 0


def test_two_users_can_vote_on_same_post(client):
    # create two users
    token1 = create_user_and_login(client, "user1@gmail.com")
    token2 = create_user_and_login(client, "user2@gmail.com")

    # user1 creates a post
    post_id = create_post(client, token1)

    # both users vote
    response1 = client.post(
        f"/vote/{post_id}", headers={"Authorization": f"Bearer {token1}"}
    )
    response2 = client.post(
        f"/vote/{post_id}", headers={"Authorization": f"Bearer {token2}"}
    )

    assert response1.json()["message"] == "Vote added successfully"
    assert response2.json()["message"] == "Vote added successfully"

    # check vote count is 2
    response = client.get(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.json()["votes"] == 2
