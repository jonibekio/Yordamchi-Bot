import asyncio
from datetime import datetime
import pytz
from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models.reminder import Reminder
from app.database.models.user import User
from app.database.session import get_db_session
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def start_reminder_scheduler(bot: Bot, interval_seconds: int = 20) -> None:
    """
    Kutilayotgan eslatmalarni o'z vaqtida foydalanuvchiga yetkazib beruvchi fon xizmati.
    """
    logger.info("Eslatmalar fon xizmati (scheduler) ishga tushdi.")
    while True:
        try:
            now_utc = datetime.now(pytz.UTC)
            async with get_db_session() as session:
                stmt = (
                    select(Reminder)
                    .options(selectinload(Reminder.user))
                    .where(
                        Reminder.is_completed == False,
                        Reminder.remind_at <= now_utc,
                    )
                    .limit(50)
                )
                result = await session.execute(stmt)
                due_reminders = result.scalars().all()

                for reminder in due_reminders:
                    try:
                        user = reminder.user
                        if user and user.is_active:
                            text = (
                                f"⏰ **Eslatma vaqti bo‘ldi!**\n\n"
                                f"📌 {reminder.text}\n\n"
                                f"🗓 Vaqt: {now_utc.astimezone(pytz.timezone(reminder.timezone)).strftime('%H:%M, %d.%m.%Y')}"
                            )
                            await bot.send_message(
                                chat_id=user.telegram_id,
                                text=text,
                                parse_mode="Markdown",
                            )

                        reminder.is_completed = True
                    except Exception as send_err:
                        logger.warning(f"Eslatmani yuborishda xato (ID: {reminder.id}): {send_err}")
                        reminder.is_completed = True  # Takrorlanishning oldini olish uchun
                
                await session.commit()
        except asyncio.CancelledError:
            logger.info("Eslatmalar fon xizmati to‘xtatildi.")
            break
        except Exception as e:
            logger.error(f"Scheduler siklida kutilmagan xatolik: {e}", exc_info=True)

        await asyncio.sleep(interval_seconds)
