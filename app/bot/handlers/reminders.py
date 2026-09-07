import pytz
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import get_reminder_item_keyboard, get_reminders_menu_keyboard
from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import ReminderStates
from app.database.models.user import User
from app.services.reminders.reminder_service import ReminderService

router = Router(name="reminders")


# 1. ➕ Yangi eslatma
@router.callback_query(F.data == "reminder_new")
async def cb_reminder_new(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReminderStates.waiting_for_reminder_text)
    await callback.message.delete()
    await callback.message.answer(
        text="⏰ **Yangi eslatma yaratish**\n\n"
             "Eslatmani vaqt bilan birga erkin o‘zbek tilida yozing.\n"
             "Masalan:\n"
             "• *'Bugun soat 20:00 da onamga qo‘ng‘iroq qilishni eslat'*\n"
             "• *'Ertaga 09:30 da dori ichish'*\n"
             "• *'15 daqiqadan keyin choyni o‘chirish'*",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(ReminderStates.waiting_for_reminder_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_reminder_text(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    status_msg = await message.answer("⏳ *Vaqt va eslatma aniqlanmoqda...*", parse_mode="Markdown")

    parsed_text, remind_at_utc = await ReminderService.parse_reminder_text(
        text=message.text,
        user_timezone_str=db_user.timezone,
    )

    await status_msg.delete()

    if not remind_at_utc:
        await message.answer(
            text="⚠️ Eslatma vaqtini aniqlab bo‘lmadi.\n"
                 "Iltimos, aniqroq vaqt ko‘rsatib qayta yozing (masalan: *'Bugun soat 18:00 da kitob o‘qish'*).",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown",
        )
        return

    reminder = await ReminderService.create_reminder(
        session=db_session,
        user_id=db_user.id,
        text=parsed_text or message.text,
        remind_at=remind_at_utc,
        timezone_str=db_user.timezone,
    )

    # Foydalanuvchiga uning o'z vaqtida chiroyli ko'rsatamiz
    user_tz = pytz.timezone(db_user.timezone)
    local_time = reminder.remind_at.astimezone(user_tz).strftime("%H:%M, %d.%m.%Y")

    await state.clear()
    await message.answer(
        text=f"✅ **Eslatma muvaffaqiyatli saqlandi!**\n\n"
             f"📌 Mazmuni: {reminder.text}\n"
             f"⏰ Vaqti: {local_time} ({db_user.timezone})",
        reply_markup=get_reminders_menu_keyboard(),
        parse_mode="Markdown",
    )


# 2. 📋 Eslatmalar ro'yxati
@router.callback_query(F.data == "reminder_list")
async def cb_reminder_list(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    reminders = await ReminderService.get_user_reminders(
        session=db_session,
        user_id=db_user.id,
        only_pending=True,
    )
    await callback.message.delete()

    if not reminders:
        await callback.message.answer(
            text="📭 Sizda hozircha faol eslatmalar yo‘q.",
            reply_markup=get_reminders_menu_keyboard(),
        )
        await callback.answer()
        return

    user_tz = pytz.timezone(db_user.timezone)
    await callback.message.answer("📋 **Sizning faol eslatmalaringiz:**", parse_mode="Markdown")

    for rem in reminders:
        local_time = rem.remind_at.astimezone(user_tz).strftime("%H:%M, %d.%m.%Y")
        text = f"📌 **{rem.text}**\n⏰ {local_time}"
        await callback.message.answer(
            text=text,
            reply_markup=get_reminder_item_keyboard(rem.id),
            parse_mode="Markdown",
        )
    await callback.answer()


# 3. 🗑 Eslatmani o'chirish
@router.callback_query(F.data.startswith("rem_del_"))
async def cb_reminder_delete(
    callback: CallbackQuery,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    rem_id = int(callback.data.split("_")[-1])
    success = await ReminderService.delete_reminder(
        session=db_session,
        user_id=db_user.id,
        reminder_id=rem_id,
    )

    if success:
        await callback.message.delete()
        await callback.message.answer("🗑 Eslatma muvaffaqiyatli o‘chirildi.")
    else:
        await callback.answer("⚠️ Eslatma topilmadi yoki allaqachon o‘chirilgan.", show_alert=True)
    await callback.answer()
