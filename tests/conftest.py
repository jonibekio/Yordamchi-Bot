import asyncio
from typing import AsyncGenerator
from unittest.mock import MagicMock
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.models.base import Base
from app.database.models.user import User

# Testlar uchun in-memory SQLite async engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> User:
    user = User(
        telegram_id=12345678,
        username="test_user",
        first_name="Testbek",
        language="uz",
        timezone="Asia/Tashkent",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def mock_openai_response():
    """Mock qilingan OpenAI chat javobi"""
    mock_resp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Bu sun’iy intellekt tomonidan qaytarilgan o‘zbekcha javob."
    mock_resp.choices = [mock_choice]
    mock_resp.usage.prompt_tokens = 25
    mock_resp.usage.completion_tokens = 40
    return mock_resp
