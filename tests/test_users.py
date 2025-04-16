import pytest

from src.services.auth import create_access_token


user_data_admin = {
    "id": 1,
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "admin",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

user_data_not_admin = {
    "id": 2,
    "username": "agent008",
    "email": "agent008@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}


@pytest.fixture
def auth_headers():
    """
    Fixture to provide valid Authorization headers.
    """
    valid_token = create_access_token({"sub": user_data_admin["username"]})
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.mark.asyncio
async def test_me_authenticated(client, monkeypatch):
    """
    Test authorized access when retrieving current user data.
    """

    response = client.get("/api/users/me")

    assert response.status_code == 200
