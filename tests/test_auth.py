def test_register_returns_user_without_password(client):
    response = client.post(
        "/auth/register", json={"username": "ana", "password": "password123"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "ana"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_username_returns_409(client):
    payload = {"username": "ana", "password": "password123"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409


def test_register_short_password_returns_422(client):
    response = client.post(
        "/auth/register", json={"username": "ana", "password": "123"}
    )

    assert response.status_code == 422


def test_login_with_wrong_password_returns_401(client):
    client.post("/auth/register", json={"username": "ana", "password": "password123"})

    response = client.post(
        "/auth/login", data={"username": "ana", "password": "incorrecta"}
    )

    assert response.status_code == 401


def test_login_unknown_user_returns_401(client):
    response = client.post(
        "/auth/login", data={"username": "nadie", "password": "password123"}
    )

    assert response.status_code == 401


def test_me_without_token_returns_401(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer token-falso"})

    assert response.status_code == 401


def test_me_returns_current_user(client, make_user):
    headers = make_user("ana")

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "ana"