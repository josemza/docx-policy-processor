def test_login_returns_tokens_and_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin12345"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["user"]["username"] == "admin"
    assert payload["data"]["tokens"]["token_type"] == "bearer"
    assert payload["data"]["tokens"]["access_token"]
    assert payload["data"]["tokens"]["refresh_token"]



def test_refresh_rotates_refresh_token(client):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin12345"},
    )
    refresh_token = login_response.json()["data"]["tokens"]["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 200
    rotated_refresh = refresh_response.json()["data"]["tokens"]["refresh_token"]
    assert rotated_refresh != refresh_token

    reused_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert reused_response.status_code == 401
    assert reused_response.json()["error"]["code"] in {"inactive_session", "refresh_token_reused"}
