def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Пользователь успешно зарегистрирован"
    }


def test_register_duplicate_user(client):
    payload = {
        "username": "testuser",
        "password": "testpassword123"
    }

    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 400


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_create_deputy_without_token(client):
    response = client.post(
        "/api/deputies",
        json={
            "full_name": "Тестовый депутат",
            "party": "Тестовая партия",
            "district": "Тестовый округ"
        }
    )

    assert response.status_code == 401

def test_create_deputy_with_token(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/deputies",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Тестовый депутат",
            "party": "Тестовая партия",
            "district": "Тестовый округ"
        }
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Тестовый депутат"
