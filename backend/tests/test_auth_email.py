import uuid


def build_signup_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"student_{suffix}",
        "email": f"student_{suffix}@example.com",
        "password": "StrongPass1!",
    }


def test_register_requires_unique_username_and_email(api_client):
    client, _ = api_client
    payload = build_signup_payload()

    first_response = client.post("/api/register", json=payload)
    assert first_response.status_code == 201
    assert first_response.json()["access_token"]

    duplicate_username = {
        "username": payload["username"],
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "StrongPass1!",
    }
    username_response = client.post("/api/register", json=duplicate_username)
    assert username_response.status_code == 400
    assert username_response.json()["detail"] == "This username is already taken."

    duplicate_email = {
        "username": f"fresh_{uuid.uuid4().hex[:8]}",
        "email": payload["email"],
        "password": "StrongPass1!",
    }
    email_response = client.post("/api/register", json=duplicate_email)
    assert email_response.status_code == 400
    assert email_response.json()["detail"] == "This email is already registered."


def test_register_rejects_weak_password(api_client):
    client, _ = api_client
    payload = build_signup_payload()
    payload["password"] = "weakpass"

    response = client.post("/api/register", json=payload)

    assert response.status_code == 422
    assert "Password must include at least 1 uppercase letter" in response.text


def test_login_accepts_email_or_username(api_client):
    client, _ = api_client
    payload = build_signup_payload()

    register_response = client.post("/api/register", json=payload)
    assert register_response.status_code == 201

    email_login = client.post(
        "/api/login",
        data={"username": payload["email"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert email_login.status_code == 200
    assert email_login.json()["access_token"]

    username_login = client.post(
        "/api/login",
        data={"username": payload["username"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert username_login.status_code == 200
    assert username_login.json()["access_token"]
