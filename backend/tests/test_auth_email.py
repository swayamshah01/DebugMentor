import uuid


def test_register_accepts_email_and_password_only(api_client):
    client, _ = api_client
    email = f"student_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/api/register",
        json={"email": email, "password": "strongpassword123"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"


def test_login_uses_email_not_username(api_client):
    client, _ = api_client
    email = f"student_{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    register_response = client.post(
        "/api/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
