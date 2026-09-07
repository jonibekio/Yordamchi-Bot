from datetime import datetime, timedelta
import pytest
import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.services.reminders.reminder_service import ReminderService


@pytest.mark.asyncio
async def test_reminders_crud(db_session: AsyncSession, sample_user: User):
    target_dt = datetime.now(pytz.UTC) + timedelta(hours=2)

    # 1. Create reminder
    reminder = await ReminderService.create_reminder(
        session=db_session,
        user_id=sample_user.id,
        text="Onamga qo‘ng‘iroq qilish",
        remind_at=target_dt,
        timezone_str="Asia/Tashkent",
    )
    assert reminder.id is not None
    assert reminder.text == "Onamga qo‘ng‘iroq qilish"
    assert reminder.is_completed is False

    # 2. Get active reminders
    reminders = await ReminderService.get_user_reminders(
        session=db_session,
        user_id=sample_user.id,
        only_pending=True,
    )
    assert len(reminders) == 1
    assert reminders[0].id == reminder.id

    # 3. Delete reminder
    deleted = await ReminderService.delete_reminder(
        session=db_session,
        user_id=sample_user.id,
        reminder_id=reminder.id,
    )
    assert deleted is True

    reminders_after = await ReminderService.get_user_reminders(
        session=db_session,
        user_id=sample_user.id,
    )
    assert len(reminders_after) == 0


@pytest.mark.asyncio
async def test_parse_reminder_fallback_minutes():
    text = "15 daqiqadan keyin choyni o‘chirish"
    parsed_text, target_dt = await ReminderService.parse_reminder_text(text)
    assert target_dt is not None
    assert "choyni o‘chirish" in parsed_text
