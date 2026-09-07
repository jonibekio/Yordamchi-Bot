from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import EducationStates
from app.database.models.user import User
from app.services.ai.service import AIService
from app.utils.message_splitter import split_text

router = Router(name="education")
ai_service = AIService()


# 1. 👨‍🏫 Menga tushuntir
@router.callback_query(F.data == "edu_explain")
async def cb_edu_explain(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EducationStates.waiting_for_explain_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="👨‍🏫 **Menga tushuntir (Feynman usuli)**\n\nQaysi mavzuni sodda qilib tushuntirib beray? Mavzuni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EducationStates.waiting_for_explain_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_explain_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Mavzu sodda va tushunarli tilda tayyorlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.explain_topic(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 2. 📝 Test tuz
@router.callback_query(F.data == "edu_quiz")
async def cb_edu_quiz(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EducationStates.waiting_for_quiz_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="📝 **Test tuzish**\n\nQaysi fan yoki mavzu bo‘yicha test savollari tuzish kerak?",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EducationStates.waiting_for_quiz_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_quiz_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Test savollari tuzilmoqda...*", parse_mode="Markdown")

    result = await ai_service.create_quiz(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 3. ❓ Savol-javob
@router.callback_query(F.data == "edu_qa")
async def cb_edu_qa(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EducationStates.waiting_for_qa_question)
    await callback.message.delete()
    await callback.message.answer(
        text="❓ **Ta’limiy savol-javob**\n\nSizni qiziqtirgan ilmiy yoki akademik savolingizni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EducationStates.waiting_for_qa_question, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_qa_question(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Javob tayyorlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.qa_education(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 4. 📚 Dars rejasini tuz
@router.callback_query(F.data == "edu_lesson")
async def cb_edu_lesson(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EducationStates.waiting_for_lesson_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="📚 **Dars rejasini tuzish**\n\nQaysi yo‘nalish yoki fan bo‘yicha to‘liq o‘quv rejasi kerak? Yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EducationStates.waiting_for_lesson_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_lesson_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Dars rejasi shakllantirilmoqda...*", parse_mode="Markdown")

    result = await ai_service.lesson_plan(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 5. 🧠 Bilimimni tekshir
@router.callback_query(F.data == "edu_check")
async def cb_edu_check(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EducationStates.waiting_for_check_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="🧠 **Bilimimni tekshir**\n\nQaysi sohada bilimlaringizni sinab ko‘rmoqchisiz? Mavzuni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(EducationStates.waiting_for_check_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_check_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Sinov savollari tuzilmoqda...*", parse_mode="Markdown")

    result = await ai_service.check_knowledge(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()
