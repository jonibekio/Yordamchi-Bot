from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import AIChatStates
from app.database.models.user import User
from app.services.ai.service import AIService
from app.utils.message_splitter import split_text

router = Router(name="ai")
ai_service = AIService()


# 1. 💬 AI bilan suhbat
@router.callback_query(F.data == "ai_chat")
async def cb_ai_chat(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIChatStates.chatting)
    await callback.message.delete()
    await callback.message.answer(
        text="💬 **AI bilan erkin suhbat**\n\n"
             "Marhamat, savolingizni yozing. Suhbat davomida xohlagancha savol berishingiz mumkin.\n"
             "Chiqish uchun **⬅️ Orqaga** tugmasini bosing.",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIChatStates.chatting, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_ai_chat_message(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *O‘ylanmoqda...*", parse_mode="Markdown")

    reply = await ai_service.chat(
        user_message=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(reply):
        await message.answer(chunk)


# 2. 💡 G‘oya yaratish
@router.callback_query(F.data == "ai_idea")
async def cb_ai_idea(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIChatStates.waiting_for_idea_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="💡 **G‘oya yaratish**\n\n"
             "Qaysi sohada yoki qanday mavzu bo‘yicha yangi g‘oyalar kerak? Mavzuni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIChatStates.waiting_for_idea_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_idea_topic(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *G‘oyalar ishlab chiqilmoqda...*", parse_mode="Markdown")

    result = await ai_service.generate_idea(
        prompt=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 3. 🎯 Qaror qabul qilish
@router.callback_query(F.data == "ai_decision")
async def cb_ai_decision(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIChatStates.waiting_for_decision_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="🎯 **Qaror qabul qilish yordamchisi**\n\n"
             "Ikkilanayotgan vaziyatingizni yozing (masalan: *'Universitetda qolish yoki ishlash'*):\n"
             "AI sizga variantlar, afzalliklar, xavflar va xolis tavsiyani tahlil qilib beradi.",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIChatStates.waiting_for_decision_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_decision_topic(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Qaror har tomonlama tahlil qilinmoqda...*", parse_mode="Markdown")

    result = await ai_service.make_decision(
        prompt=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 4. 🧠 Fikrni tahlil qilish
@router.callback_query(F.data == "ai_thought")
async def cb_ai_thought(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIChatStates.waiting_for_thought)
    await callback.message.delete()
    await callback.message.answer(
        text="🧠 **Fikrni tahlil qilish**\n\n"
             "Tahlil qilmoqchi bo‘lgan fikringiz, gipotezangiz yoki mulohazangizni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIChatStates.waiting_for_thought, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_thought(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Fikr tahlil qilinmoqda...*", parse_mode="Markdown")

    result = await ai_service.analyze_thought(
        prompt=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 5. 🔎 Muammoni tahlil qilish
@router.callback_query(F.data == "ai_problem")
async def cb_ai_problem(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIChatStates.waiting_for_problem)
    await callback.message.delete()
    await callback.message.answer(
        text="🔎 **Muammoni tahlil qilish**\n\n"
             "Duch kelgan muammoni batafsil tasvirlab bering (ildiz sabablari va yechimlar ko‘rsatiladi):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIChatStates.waiting_for_problem, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_problem(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Muammo o‘rganilmoqda...*", parse_mode="Markdown")

    result = await ai_service.analyze_problem(
        prompt=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 6. 🧑‍💻 Dasturlash yordamchisi
@router.callback_query(F.data == "ai_coding")
async def cb_ai_coding(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AIChatStates.waiting_for_coding_question)
    await callback.message.delete()
    await callback.message.answer(
        text="🧑‍💻 **Dasturlash yordamchisi**\n\n"
             "Kodingizni, xatolik matnini yoki dasturlashga oid savolingizni yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(AIChatStates.waiting_for_coding_question, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_coding_question(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Kod tahlil qilinmoqda...*", parse_mode="Markdown")

    result = await ai_service.coding_assistant(
        prompt=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()
