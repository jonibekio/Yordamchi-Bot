import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from app.bot.handlers import get_main_router
from app.bot.middlewares import LoggingMiddleware, RateLimitMiddleware, UserMiddleware
from app.config.settings import get_settings
from app.database.session import close_db, init_db
from app.services.reminders.scheduler import start_reminder_scheduler
from app.utils.logger import setup_logger

logger = setup_logger("main")
settings = get_settings()


async def main() -> None:
    logger.info("O‘zbek AI Yordamchi Telegram boti ishga tushirilmoqda...")

    # 1. Token tekshiruvi
    if (
        not settings.BOT_TOKEN
        or "bu_yerga" in settings.BOT_TOKEN
        or settings.BOT_TOKEN == "mock_token"
        or ":" not in settings.BOT_TOKEN
    ):
        logger.error(
            "\n"
            "==================================================================\n"
            "❌ BOT_TOKEN kiritilmagan yoki noto‘g‘ri!\n"
            "👉 Iltimos, .env faylini oching va quyidagi qatorga haqiqiy tokenni yozing:\n"
            "   BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ\n"
            "Tokenni Telegram'dagi @BotFather orqali olishingiz mumkin.\n"
            "=================================================================="
        )
        sys.exit(1)

    from app.services.ai.client import is_gemini_active, get_active_model

    if is_gemini_active():
        logger.info(f"✨ AI Provayder: Google Gemini ({get_active_model()}) muvaffaqiyatli ulandi.")
    elif settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("bu_yerga") and settings.OPENAI_API_KEY != "mock_key":
        logger.info(f"✨ AI Provayder: OpenAI ({get_active_model()}) ulandi.")
    else:
        logger.warning(
            "⚠️ DIQQAT: GEMINI_API_KEY .env faylida kiritilmagan. Sun’iy intellekt funksiyalari ishlashi uchun kalit kiritishingiz lozim."
        )

    # 2. Bazani initsializatsiya qilish
    try:
        await init_db()
        logger.info("Ma'lumotlar bazasi jadvallari muvaffaqiyatli tekshirildi.")
    except Exception as e:
        logger.error(f"Bazani initsializatsiya qilishda xatolik: {e}")
        sys.exit(1)

    # 3. Redis FSM Storage
    storage = MemoryStorage()
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        await redis_client.ping()
        storage = RedisStorage(redis=redis_client)
        logger.info("Redis FSM storage ulandi.")
    except Exception as e:
        logger.info(f"Redis ulanmadi ({e}), xavfsiz MemoryStorage ishlatiladi.")
        storage = MemoryStorage()

    # 4. Bot va Dispatcher yaratish
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # 5. Middlewarelarni ro'yxatdan o'tkazish
    dp.message.outer_middleware(LoggingMiddleware())
    dp.callback_query.outer_middleware(LoggingMiddleware())

    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # 6. Asosiy Routerni ulash
    dp.include_router(get_main_router())

    # 7. Eslatmalar fon xizmatini (scheduler) ishga tushirish
    scheduler_task = asyncio.create_task(start_reminder_scheduler(bot=bot, interval_seconds=20))

    try:
        logger.info("Bot polling rejimi boshlandi.")
        # Eski update'larni o'tkazib yuborish
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot ishlashida xatolik: {e}", exc_info=True)
    finally:
        logger.info("Bot to‘xtatilmoqda...")
        scheduler_task.cancel()
        await bot.session.close()
        await close_db()
        logger.info("Barcha resurslar toza yopildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to‘xtatildi.")
