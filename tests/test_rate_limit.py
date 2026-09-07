from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from aiogram.types import Message, User as TgUser

from app.bot.middlewares.rate_limit import RateLimitMiddleware


@pytest.mark.asyncio
async def test_rate_limit_within_limit():
    middleware = RateLimitMiddleware()

    # Mock redis client
    mock_redis = AsyncMock()
    mock_redis.incr = AsyncMock(return_value=5)  # 5 requests (below limit 20)
    mock_redis.expire = AsyncMock()

    # Mock event
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()
    user = TgUser(id=12345, is_bot=False, first_name="Ali")
    data = {"event_from_user": user}

    handler = AsyncMock(return_value="handler_called")

    with patch("app.bot.middlewares.rate_limit.get_redis", return_value=mock_redis):
        result = await middleware(handler, message, data)
        assert result == "handler_called"
        handler.assert_awaited_once()
        message.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    middleware = RateLimitMiddleware()

    mock_redis = AsyncMock()
    mock_redis.incr = AsyncMock(return_value=25)  # Exceeds limit of 20
    mock_redis.expire = AsyncMock()

    message = MagicMock(spec=Message)
    message.answer = AsyncMock()
    user = TgUser(id=12345, is_bot=False, first_name="Ali")
    data = {"event_from_user": user}

    handler = AsyncMock(return_value="handler_called")

    with patch("app.bot.middlewares.rate_limit.get_redis", return_value=mock_redis):
        result = await middleware(handler, message, data)
        assert result is None
        handler.assert_not_awaited()
        message.answer.assert_awaited_once()
        args, _ = message.answer.call_args
        assert "juda ko‘p so‘rov" in args[0]
