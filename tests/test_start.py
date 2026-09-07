from unittest.mock import AsyncMock, MagicMock
import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Chat, Message, User as TgUser

from app.bot.handlers.start import START_WELCOME_TEXT, cmd_start


@pytest.mark.asyncio
async def test_cmd_start():
    # Mock message
    message = MagicMock(spec=Message)
    message.text = "/start"
    message.from_user = TgUser(id=999, is_bot=False, first_name="Ali", username="alijon")
    message.chat = Chat(id=999, type="private")
    message.answer = AsyncMock()

    # Mock FSM state
    state = MagicMock(spec=FSMContext)
    state.clear = AsyncMock()

    await cmd_start(message=message, state=state)

    state.clear.assert_awaited_once()
    message.answer.assert_awaited_once()
    args, kwargs = message.answer.call_args
    assert START_WELCOME_TEXT in kwargs.get("text", "")
    assert kwargs.get("reply_markup") is not None
