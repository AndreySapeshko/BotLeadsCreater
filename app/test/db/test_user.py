import pytest

from app.db.crud import get_or_create_user


@pytest.mark.asyncio
async def test_get_or_create_user_creates(session):
    user = await get_or_create_user(
        session,
        telegram_id=123,
        username="testuser",
    )

    assert user.id is not None
    assert user.telegram_id == 123
    assert user.username == "testuser"
