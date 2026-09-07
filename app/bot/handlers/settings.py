import pytz
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard, get_main_menu_keyboard
from app.bot.states.states import SettingsStates
from app.database.models.user import User
from app.services.ai.service import AIService

router = Router(name="settings")
ai_service = AIService()


# 1. 🌍 Vaqt mintaqasini o'zgartirish
@router.callback_query(F.data == "settings_tz")
async def cb_settings_tz(callback: CallbackQuery, state: FSMContext, db_user: User) -> None:
    await state.set_state(SettingsStates.waiting_for_timezone)
    await callback.message.delete()
    await callback.message.answer(
        text=f"🌍 **Vaqt mintaqasi**\n\n"
             f"Hozirgi vaqt mintaqangiz: `{db_user.timezone}`\n\n"
             "Yangi vaqt mintaqasini kiriting (masalan: *Asia/Tashkent*, *Europe/Moscow*, *UTC*):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_timezone, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_timezone_input(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    new_tz_str = message.text.strip()
    try:
        pytz.timezone(new_tz_str)
    except Exception:
        await message.answer(
            "⚠️ Noto‘g‘ri vaqt mintaqasi kiritildi. Iltimos, to‘g‘ri formatda kiriting (masalan: `Asia/Tashkent`):",
            parse_mode="Markdown",
        )
        return

    db_user.timezone = new_tz_str
    await db_session.commit()
    await state.clear()

    await message.answer(
        f"✅ Vaqt mintaqangiz muvaffaqiyatli o‘zgartirildi: `{new_tz_str}`",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


# 2. 🔄 Suhbat tarixini tozalash (Yangi suhbat)
@router.callback_query(F.data == "settings_clear_chat")
async def cb_settings_clear_chat(
    callback: CallbackQuery,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    success = await ai_service.clear_chat_history(user_id=db_user.id, session=db_session)
    await callback.message.delete()

    if success:
        await callback.message.answer(
            "🔄 **Suhbat tarixi muvaffaqiyatli tozalandi!**\n\nEndi sun’iy intellekt bilan toza sahifadan suhbat boshlashingiz mumkin.",
            parse_mode="Markdown",
        )
    else:
        await callback.message.answer("⚠️ Suhbat tarixini tozalashda xatolik yuz berdi.")
    await callback.answer()
