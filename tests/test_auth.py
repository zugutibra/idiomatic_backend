def test_signup_then_access_protected_endpoint(client):
    resp = client.post(
        "/auth/signup",
        json={"email": "a@example.com", "password": "secret123", "display_name": "A"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]

    protected = client.get("/progress/stats", headers={"Authorization": f"Bearer {token}"})
    assert protected.status_code == 200


def test_signup_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "password": "secret123", "display_name": "A"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 400


def test_login_then_access_protected_endpoint(client):
    client.post(
        "/auth/signup",
        json={"email": "b@example.com", "password": "secret123", "display_name": "B"},
    )
    resp = client.post("/auth/login", json={"email": "b@example.com", "password": "secret123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    protected = client.get("/progress/stats", headers={"Authorization": f"Bearer {token}"})
    assert protected.status_code == 200


def test_login_wrong_password_rejected(client):
    client.post(
        "/auth/signup",
        json={"email": "c@example.com", "password": "secret123", "display_name": "C"},
    )
    resp = client.post("/auth/login", json={"email": "c@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_protected_endpoint_rejects_missing_token(client):
    resp = client.get("/progress/stats")
    assert resp.status_code == 401


def test_protected_endpoint_rejects_invalid_token(client):
    resp = client.get("/progress/stats", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
