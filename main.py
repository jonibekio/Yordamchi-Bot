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

    # 1. Bazani initsializatsiya qilish
    try:
        await init_db()
        logger.info("Ma'lumotlar bazasi jadvallari muvaffaqiyatli tekshirildi.")
    except Exception as e:
        logger.error(f"Bazani initsializatsiya qilishda xatolik: {e}")
        sys.exit(1)

    # 2. Redis FSM Storage
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL)
        storage = RedisStorage(redis=redis_client)
        logger.info("Redis FSM storage ulandi.")
    except Exception as e:
        logger.warning(f"Redis ulanmadi ({e}), MemoryStorage ishlatiladi.")
        storage = MemoryStorage()

    # 3. Bot va Dispatcher yaratish
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # 4. Middlewarelarni ro'yxatdan o'tkazish
    dp.message.outer_middleware(LoggingMiddleware())
    dp.callback_query.outer_middleware(LoggingMiddleware())

    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # 5. Asosiy Routerni ulash
    dp.include_router(get_main_router())

    # 6. Eslatmalar fon xizmatini (scheduler) ishga tushirish
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
        logger.info("Bot qo‘lda to‘xtatildi.")
