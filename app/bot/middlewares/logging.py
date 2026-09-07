from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Botga kelayotgan xabarlar va callbacklarni qayd etuvchi (logging) middleware.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        user_info = f"User[{user.id} - @{user.username}]" if user else "Anonim"

        if isinstance(event, Message):
            content_type = event.content_type
            if event.text:
                logger.info(f"{user_info} matn yubordi: {event.text[:50]}")
            else:
                logger.info(f"{user_info} {content_type} yubordi")
        elif isinstance(event, CallbackQuery):
            logger.info(f"{user_info} callback bosdi: {event.data}")

        return await handler(event, data)
