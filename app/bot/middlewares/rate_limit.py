from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
import redis.asyncio as aioredis

from app.config.settings import get_settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

_redis_client: Optional[aioredis.Redis] = None
_redis_checked: bool = False


async def get_redis() -> Optional[aioredis.Redis]:
    global _redis_client, _redis_checked
    if not _redis_checked:
        _redis_checked = True
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=1.0,
            )
            await client.ping()
            _redis_client = client
        except Exception as e:
            logger.debug(f"Redis ulanishida xatolik (Rate limiter o'tkazib yuboriladi): {e}")
            _redis_client = None
    return _redis_client


class RateLimitMiddleware(BaseMiddleware):
    """
    Foydalanuvchi so'rovlarini cheklovchi (Rate limiting) middleware.
    Bir daqiqada belgilangan miqdordan ortiq so'rov yuborilganda to'xtatadi.
    Agar Redis mavjud bo'lmasa, so'rovlarni erkin o'tkazadi.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user or user.is_bot:
            return await handler(event, data)

        redis_client = await get_redis()
        if redis_client is not None:
            try:
                key = f"rate_limit:{user.id}"
                current_requests = await redis_client.incr(key)
                if current_requests == 1:
                    await redis_client.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)

                if current_requests > settings.RATE_LIMIT_REQUESTS:
                    msg_text = "⚠️ Siz juda ko‘p so‘rov yubordingiz. Iltimos, bir oz kuting."
                    if isinstance(event, Message):
                        await event.answer(msg_text)
                    elif isinstance(event, CallbackQuery):
                        await event.answer(msg_text, show_alert=True)
                    return None
            except Exception as e:
                logger.debug(f"Rate limiter xatoligi: {e}")

        return await handler(event, data)
