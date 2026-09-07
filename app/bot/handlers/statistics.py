from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_STATS
from app.database.models.ai_usage import AIUsage
from app.database.models.note import Note
from app.database.models.reminder import Reminder
from app.database.models.user import User

router = Router(name="statistics")


@router.message(F.text == BTN_STATS)
async def show_user_statistics(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await state.clear()

    # 1. AI Usage
    usage_stmt = select(
        func.count(AIUsage.id),
        func.sum(AIUsage.input_tokens),
        func.sum(AIUsage.output_tokens),
    ).where(AIUsage.user_id == db_user.id)
    usage_res = await db_session.execute(usage_stmt)
    total_requests, total_input, total_output = usage_res.one()

    total_requests = total_requests or 0
    total_input = total_input or 0
    total_output = total_output or 0

    # 2. Qaydlar soni
    notes_stmt = select(func.count(Note.id)).where(Note.user_id == db_user.id)
    notes_res = await db_session.execute(notes_stmt)
    total_notes = notes_res.scalar_one() or 0

    # 3. Faol eslatmalar soni
    rem_stmt = select(func.count(Reminder.id)).where(
        Reminder.user_id == db_user.id,
        Reminder.is_completed == False,
    )
    rem_res = await db_session.execute(rem_stmt)
    total_reminders = rem_res.scalar_one() or 0

    reg_date = db_user.created_at.strftime("%d.%m.%Y") if db_user.created_at else "Noma'lum"

    stats_text = (
        "📊 **Sizning faoliyatingiz statistikasi**\n\n"
        f"👤 Foydalanuvchi: **{db_user.first_name or 'Foydalanuvchi'}**\n"
        f"📅 Ro‘yxatdan o‘tilgan: {reg_date}\n"
        f"🌍 Vaqt mintaqasi: `{db_user.timezone}`\n\n"
        "🤖 **Sun’iy intellekt:**\n"
        f"• Jami AI so‘rovlar: **{total_requests} ta**\n"
        f"• Ishlatilgan tokenlar: **{total_input + total_output:,}** "
        f"*(kirish: {total_input:,}, chiqish: {total_output:,})*\n\n"
        "📝 **Shaxsiy vositalar:**\n"
        f"• Saqlangan qaydlar: **{total_notes} ta**\n"
        f"• Faol eslatmalar: **{total_reminders} ta**\n\n"
        "💡 *O‘zbek AI Yordamchi xizmatidan faol foydalanayotganingiz uchun rahmat!*"
    )

    await message.answer(stats_text, parse_mode="Markdown")
