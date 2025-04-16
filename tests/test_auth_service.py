import pytest
import json
from datetime import datetime, timezone
from jose import jwt
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.auth import (
    create_access_token,
    get_current_user,
    get_email_from_token,
    get_password_from_token,
    create_email_token,
    get_admin_user
)
from src.conf.config import config
from src.db.models import User, Role


@pytest.fixture
def fake_user():
    return User(
        id=1,
        username="johndoe",
        email="johndoe@example.com",
        hashed_password="hashedpassword",
        created_at=datetime.now(timezone.utc),
        avatar="avatar.png",
        confirmed=True,
        role=Role.USER
    )


@pytest.mark.asyncio
async def test_create_access_token_contains_subject():
    data = {"sub": "johndoe"}
    token = await create_access_token(data, expires_delta=60)
    decoded = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    assert decoded["sub"] == "johndoe"
    assert "exp" in decoded


def test_create_email_token_and_decode():
    data = {"sub": "johndoe@example.com"}
    token = create_email_token(data)
    decoded = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    assert decoded["sub"] == "johndoe@example.com"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_get_email_from_token_valid():
    email = "test@example.com"
    token = jwt.encode({"sub": email}, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    result = await get_email_from_token(token)
    assert result == email


@pytest.mark.asyncio
async def test_get_email_from_token_invalid():
    with pytest.raises(HTTPException):
        await get_email_from_token("invalid.token.value")


@pytest.mark.asyncio
async def test_get_password_from_token_valid():
    token = jwt.encode({"password": "mysecret"}, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    password = await get_password_from_token(token)
    assert password == "mysecret"


@pytest.mark.asyncio
async def test_get_password_from_token_invalid():
    with pytest.raises(HTTPException):
        await get_password_from_token("invalid.token.value")


@pytest.mark.asyncio
@patch("src.services.auth.redis_client.get", new_callable=AsyncMock)
@patch("src.services.auth.redis_client.set", new_callable=AsyncMock)
@patch("src.services.auth.UserService.get_user_by_username", new_callable=AsyncMock)
async def test_get_current_user_from_db_and_cache(mock_get_user, mock_redis_set, mock_redis_get, fake_user):
    mock_redis_get.return_value = None
    mock_get_user.return_value = fake_user

    token = jwt.encode({"sub": fake_user.username}, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    db_mock = MagicMock()

    user = await get_current_user(token=token, db=db_mock)
    assert user.username == fake_user.username
    mock_redis_set.assert_called()


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException):
        await get_current_user(token="invalid.token", db=MagicMock())


def test_get_admin_user_with_admin():
    admin_user = User(id=1, username="admin", email="admin@test.com", role=Role.ADMIN)
    assert get_admin_user(current_user=admin_user) == admin_user


def test_get_admin_user_with_non_admin():
    user = User(id=1, username="john", email="john@test.com", role=Role.USER)
    with pytest.raises(HTTPException):
        get_admin_user(current_user=user)
