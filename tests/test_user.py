import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


@pytest.mark.asyncio
async def test_user_creation_and_attributes(db_session: AsyncSession):
    new_user = User(
        telegram_id=987654321,
        username="valijon",
        first_name="Vali",
        language="uz",
        timezone="Asia/Tashkent",
        is_active=True,
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    assert new_user.id is not None
    assert new_user.telegram_id == 987654321
    assert new_user.language == "uz"
    assert new_user.timezone == "Asia/Tashkent"
    assert new_user.is_active is True

    # Qayta o'qish
    stmt = select(User).where(User.telegram_id == 987654321)
    res = await db_session.execute(stmt)
    found = res.scalar_one_or_none()
    assert found is not None
    assert found.username == "valijon"
