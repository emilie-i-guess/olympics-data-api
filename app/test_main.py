from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_user():
    # Test to see if we can make a user and get 100 tokens
    response = client.post(
        "/v1/user", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["tokens"] == 100
    assert "user_id" in data
    return data["user_id"]


def test_token_reduction():
    # Making new unique user for test
    user_res = client.post(
        "/v1/user", json={"email": "token_test@example.com", "password": "password"}
    )
    user_id = user_res.json()["user_id"]

    # Calling data endpoint
    response = client.get(f"/v1/sport/Ski%20Jumping?user_id={user_id}")

    # Check if we got some data and tokens being reduced to 99
    assert response.status_code == 200
    assert response.json()["remaining_tokens"] == 99


# Check for error message with 0 tokens
def test_out_of_tokens():
    # Easy testing with sending invalid user_id
    response = client.get("/v1/sport/Ski%20Jumping?user_id=not-found")
    assert response.status_code == 404
