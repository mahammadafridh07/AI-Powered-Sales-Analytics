def test_register_new_user(client):
    res = client.post("/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "password": "AlicePass123",
    })
    assert res.status_code == 201
    body = res.json()
    assert "access_token" in body
    assert body["user"]["email"] == "alice@example.com"


def test_register_duplicate_email_fails(client):
    client.post("/auth/register", json={"name": "Bob", "email": "bob@example.com", "password": "BobPass123"})
    res = client.post("/auth/register", json={"name": "Bob2", "email": "bob@example.com", "password": "BobPass123"})
    assert res.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"name": "Carl", "email": "carl@example.com", "password": "CarlPass123"})
    res = client.post("/auth/login", json={"email": "carl@example.com", "password": "CarlPass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"name": "Dana", "email": "dana@example.com", "password": "DanaPass123"})
    res = client.post("/auth/login", json={"email": "dana@example.com", "password": "WrongPassword"})
    assert res.status_code == 401


def test_protected_route_requires_token(client):
    res = client.get("/dashboard/summary")
    assert res.status_code == 401


def test_me_endpoint(client, auth_headers):
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "tester@example.com"
