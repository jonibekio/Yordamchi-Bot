from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.config.settings import get_settings

settings = get_settings()


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id == settings.ADMIN_ID
