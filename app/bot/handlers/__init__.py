from aiogram import Router

from app.bot.handlers.start import router as start_router
from app.bot.handlers.ai import router as ai_router
from app.bot.handlers.text import router as text_router
from app.bot.handlers.image import router as image_router
from app.bot.handlers.voice import router as voice_router
from app.bot.handlers.documents import router as documents_router
from app.bot.handlers.education import router as education_router
from app.bot.handlers.entertainment import router as entertainment_router
from app.bot.handlers.notes import router as notes_router
from app.bot.handlers.reminders import router as reminders_router
from app.bot.handlers.statistics import router as statistics_router
from app.bot.handlers.settings import router as settings_router
from app.bot.handlers.admin import router as admin_router


def get_main_router() -> Router:
    main_router = Router(name="main_router")

    # Handlerlar tartibi muhim
    main_router.include_router(admin_router)
    main_router.include_router(start_router)
    main_router.include_router(ai_router)
    main_router.include_router(text_router)
    main_router.include_router(image_router)
    main_router.include_router(voice_router)
    main_router.include_router(documents_router)
    main_router.include_router(education_router)
    main_router.include_router(entertainment_router)
    main_router.include_router(notes_router)
    main_router.include_router(reminders_router)
    main_router.include_router(statistics_router)
    main_router.include_router(settings_router)

    return main_router


__all__ = ["get_main_router"]
