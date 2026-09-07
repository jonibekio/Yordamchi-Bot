from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy import select

from app.database.models.user import User
from app.database.session import get_db_session
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    Foydalanuvchini har bir so'rovda bazadan qidirib, agar bo'lmasa yaratuvchi,
    bo'lsa ma'lumotlarini yangilovchi va session hamda user obyektini handlerga uzatuvchi middleware.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: TgUser = data.get("event_from_user")
        if not tg_user or tg_user.is_bot:
            return await handler(event, data)

        async with get_db_session() as session:
            try:
                stmt = select(User).where(User.telegram_id == tg_user.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    user = User(
                        telegram_id=tg_user.id,
                        username=tg_user.username,
                        first_name=tg_user.first_name,
                        language="uz",
                        timezone="Asia/Tashkent",
                        is_active=True,
                    )
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                else:
                    # Ma'lumotlar o'zgargan bo'lsa yangilaymiz
                    updated = False
                    if user.username != tg_user.username:
                        user.username = tg_user.username
                        updated = True
                    if user.first_name != tg_user.first_name:
                        user.first_name = tg_user.first_name
                        updated = True
                    if updated:
                        await session.commit()

                data["db_user"] = user
                data["db_session"] = session
            except Exception as e:
                logger.error(f"UserMiddleware xatosi: {e}", exc_info=True)

            return await handler(event, data)
