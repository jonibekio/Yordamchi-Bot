from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import EntertainmentStates
from app.database.models.user import User
from app.services.ai.service import AIService
from app.utils.message_splitter import split_text

router = Router(name="entertainment")
ai_service = AIService()


# 1. 😂 Meni kuldir
@router.callback_query(F.data == "ent_laugh")
async def cb_ent_laugh(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ *Qiziqarli hazil tayyorlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.make_me_laugh(user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(f"😂 **Hazil vaqti:**\n\n{result}"):
        await callback.message.answer(chunk, parse_mode="Markdown")
    await callback.answer()


# 2. 🔥 Meni tanqid qil (Roast)
@router.callback_query(F.data == "ent_roast")
async def cb_ent_roast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EntertainmentStates.waiting_for_roast_info)
    await callback.message.delete()
    await callback.message.answer(
        text="🔥 **Meni tanqid qil (Do‘stona roast)**\n\n"
             "O‘zingiz, odatlaringiz yoki kasbingiz haqida qisqacha yozing (AI sizni hazilomuz tanqid qiladi):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EntertainmentStates.waiting_for_roast_info, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_roast_info(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *O‘tkir tanqid tayyorlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.roast_me(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(f"🔥 **Do‘stona tanqid:**\n\n{result}"):
        await message.answer(chunk, parse_mode="Markdown")
    await state.clear()


# 3. 🎭 Xarakterimni tahlil qil
@router.callback_query(F.data == "ent_personality")
async def cb_ent_personality(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EntertainmentStates.waiting_for_personality_text)
    await callback.message.delete()
    await callback.message.answer(
        text="🎭 **Xarakterimni tahlil qil**\n\n"
             "O‘zingizning fe'l-atvoringiz, qiziqishlaringiz va odatlaringiz haqida bir necha jumla yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EntertainmentStates.waiting_for_personality_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_personality_text(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Xarakteringiz psixologik tahlil qilinmoqda...*", parse_mode="Markdown")

    result = await ai_service.analyze_personality(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(f"🎭 **Xarakter tahlili:**\n\n{result}"):
        await message.answer(chunk, parse_mode="Markdown")
    await state.clear()


# 4. 🎲 Tasodifiy topshiriq
@router.callback_query(F.data == "ent_challenge")
async def cb_ent_challenge(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ *Bugungi topshiriq tanlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.generate_challenge(user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(f"🎲 **Bugungi topshiriq:**\n\n{result}"):
        await callback.message.answer(chunk, parse_mode="Markdown")
    await callback.answer()


# 5. 🕵️ Sirli vazifa
@router.callback_query(F.data == "ent_mystery")
async def cb_ent_mystery(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ *Sirli jumboq tuzilmoqda...*", parse_mode="Markdown")

    result = await ai_service.mystery_task(user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(f"🕵️ **Sirli vazifa:**\n\n{result}"):
        await callback.message.answer(chunk, parse_mode="Markdown")
    await callback.answer()


# 6. ⚔️ Qarorlar jangi
@router.callback_query(F.data == "ent_battle")
async def cb_ent_battle(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EntertainmentStates.waiting_for_battle_choices)
    await callback.message.delete()
    await callback.message.answer(
        text="⚔️ **Qarorlar jangi**\n\nTo‘qnashtirmoqchi bo‘lgan 2 ta variantingizni yozing (masalan: *'iPhone yoki Android'*):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EntertainmentStates.waiting_for_battle_choices, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_battle_choices(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Qarorlar jangi baholanmoqda...*", parse_mode="Markdown")

    result = await ai_service.decision_battle(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(f"⚔️ **Jang natijasi:**\n\n{result}"):
        await message.answer(chunk, parse_mode="Markdown")
    await state.clear()
