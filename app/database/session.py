from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings
from app.database.models.base import Base

logger = logging.getLogger("database")
settings = get_settings()

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
_current_db_url: str = settings.DATABASE_URL


def _build_engine(db_url: str) -> AsyncEngine:
    kwargs = {"echo": settings.DEBUG}
    if not db_url.startswith("sqlite"):
        kwargs["pool_pre_ping"] = True
    return create_async_engine(db_url, **kwargs)


def get_engine() -> AsyncEngine:
    global _engine, _current_db_url
    if _engine is None:
        _engine = _build_engine(_current_db_url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    global _engine, _session_factory, _current_db_url
    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Agar PostgreSQL ga ulanishda xato (masalan parol noto'g'ri) bo'lsa,
        # dasturni to'xtatib qo'ymasdan mahalliy SQLite bazasiga avtomatik o'tamiz
        logger.warning(
            f"⚠️ Asosiy bazaga ({_current_db_url}) ulanishda xatolik: {e}.\n"
            f"Mahalliy 'sqlite+aiosqlite:///bot.db' bazasiga avtomatik o‘tilmoqda..."
        )
        if _engine is not None:
            await _engine.dispose()

        _current_db_url = "sqlite+aiosqlite:///bot.db"
        _engine = _build_engine(_current_db_url)
        _session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ SQLite bazasi muvaffaqiyatli ishga tushirildi va jadvallar yaratildi.")


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
