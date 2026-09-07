import json
import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import pytz
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.models.reminder import Reminder
from app.services.ai.client import get_openai_client
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


class ReminderService:
    @staticmethod
    async def parse_reminder_text(
        text: str,
        user_timezone_str: str = "Asia/Tashkent",
    ) -> Tuple[Optional[str], Optional[datetime]]:
        """
        OpenAI yordamida erkin o'zbekcha matndan eslatma mazmuni va vaqtini (ISO format) ajratib olish.
        Fallback sifatida regex qoidalarini qo'llaydi.
        """
        try:
            tz = pytz.timezone(user_timezone_str)
        except Exception:
            tz = pytz.timezone(settings.DEFAULT_TIMEZONE)

        now_local = datetime.now(tz)
        current_time_str = now_local.strftime("%Y-%m-%d %H:%M")

        system_prompt = (
            f"Siz vaqt va eslatmalarni tahlil qiluvchi yordamchisiz.\n"
            f"Foydalanuvchining joriy mahalliy vaqti: {current_time_str}, mintaqa: {user_timezone_str}.\n"
            f"Foydalanuvchi eslatma yozadi (masalan: 'Bugun soat 20:00 da onamga qo‘ng‘iroq qilishni eslat' yoki 'Ertaga 09:00 da dori ichish').\n"
            f"Vazifangiz faqat quyidagi JSON formatida javob qaytarish:\n"
            f'{{"text": "Eslatma matni", "remind_at": "YYYY-MM-DD HH:MM:SS"}}\n'
            f"Agar vaqtni mutlaqo aniqlab bo'lmasa, remind_at qiymatini null qiling.\n"
            f"Boshqa hech qanday so‘z yoki markdown qo‘shmang, faqat toza JSON."
        )

        client = get_openai_client()
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                max_tokens=200,
            )
            raw_json = (response.choices[0].message.content or "").strip()
            # Clean markdown code blocks if present
            if raw_json.startswith("```"):
                raw_json = re.sub(r"^```[a-zA-Z]*\n?", "", raw_json)
                raw_json = re.sub(r"\n?```$", "", raw_json)

            data = json.loads(raw_json)
            parsed_text = data.get("text", text)
            remind_at_str = data.get("remind_at")

            if remind_at_str:
                dt_naive = datetime.strptime(remind_at_str, "%Y-%m-%d %H:%M:%S")
                dt_aware = tz.localize(dt_naive)
                # UTC ga o'tkazish
                dt_utc = dt_aware.astimezone(pytz.UTC)
                return parsed_text, dt_utc
        except Exception as e:
            logger.warning(f"AI orqali eslatma vaqtini aniqlashda xato: {e}. Fallback ishlatilmoqda.")

        # Fallback: Oddiy "X daqiqadan keyin" yoki "X soatdan keyin" tekshiruvi
        m_min = re.search(r"(\d+)\s*(daqiqa|minut)", text, re.IGNORECASE)
        m_hour = re.search(r"(\d+)\s*(soat)", text, re.IGNORECASE)
        delta = None
        clean_text = text

        if m_min:
            mins = int(m_min.group(1))
            delta = timedelta(minutes=mins)
            clean_text = text.replace(m_min.group(0), "").strip()
        elif m_hour:
            hours = int(m_hour.group(1))
            delta = timedelta(hours=hours)
            clean_text = text.replace(m_hour.group(0), "").strip()

        if delta:
            target_dt_utc = datetime.now(pytz.UTC) + delta
            return clean_text or text, target_dt_utc

        return None, None

    @staticmethod
    async def create_reminder(
        session: AsyncSession,
        user_id: int,
        text: str,
        remind_at: datetime,
        timezone_str: str = "Asia/Tashkent",
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            text=text.strip(),
            remind_at=remind_at,
            timezone=timezone_str,
            is_completed=False,
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder

    @staticmethod
    async def get_user_reminders(
        session: AsyncSession,
        user_id: int,
        only_pending: bool = True,
        limit: int = 15,
    ) -> List[Reminder]:
        stmt = select(Reminder).where(Reminder.user_id == user_id)
        if only_pending:
            stmt = stmt.where(Reminder.is_completed == False)
        stmt = stmt.order_by(Reminder.remind_at.asc()).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_reminder(
        session: AsyncSession,
        user_id: int,
        reminder_id: int,
    ) -> bool:
        stmt = delete(Reminder).where(Reminder.id == reminder_id, Reminder.user_id == user_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
