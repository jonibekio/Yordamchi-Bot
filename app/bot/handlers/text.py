from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import TextStates
from app.database.models.user import User
from app.services.ai.service import AIService
from app.utils.message_splitter import split_text

router = Router(name="text")
ai_service = AIService()


# 1. 📝 Matn yozish
@router.callback_query(F.data == "text_write")
async def cb_text_write(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_write_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="📝 **Matn yozish**\n\nQanday mavzuda matn yozib beray? Mavzuni va kerakli talablarni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_write_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_write_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Matn yozilmoqda...*", parse_mode="Markdown")

    result = await ai_service.write_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 2. ✨ Matnni yaxshilash
@router.callback_query(F.data == "text_improve")
async def cb_text_improve(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_improve_text)
    await callback.message.delete()
    await callback.message.answer(
        text="✨ **Matnni yaxshilash**\n\nYaxshilamoqchi bo‘lgan matningizni yuboring (grammatika va uslub to‘g‘rilanadi):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_improve_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_improve_text(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Matn tahrir qilinmoqda...*", parse_mode="Markdown")

    result = await ai_service.improve_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 3. 📌 Matnni qisqartirish
@router.callback_query(F.data == "text_summarize")
async def cb_text_summarize(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_summarize_text)
    await callback.message.delete()
    await callback.message.answer(
        text="📌 **Matnni qisqartirish**\n\nQisqartirmoqchi bo‘lgan uzun matningizni yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_summarize_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_summarize_text(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Matn qisqartirilmoqda...*", parse_mode="Markdown")

    result = await ai_service.summarize_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 4. 🔄 Qayta yozish
@router.callback_query(F.data == "text_rewrite")
async def cb_text_rewrite(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_rewrite_text)
    await callback.message.delete()
    await callback.message.answer(
        text="🔄 **Matnni qayta yozish**\n\nBoshqa uslubda qayta yozilishi kerak bo‘lgan matnni yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_rewrite_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_rewrite_text(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Matn qayta ishlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.rewrite_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 5. 🌐 Tarjima qilish
@router.callback_query(F.data == "text_translate")
async def cb_text_translate(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_translate_text)
    await callback.message.delete()
    await callback.message.answer(
        text="🌐 **Tarjima qilish**\n\n"
             "Tarjima qilinadigan matnni yuboring. Agar kerak bo‘lsa qaysi tilga ekanligini ham ko‘rsating "
             "(masalan: *'Ingliz tiliga tarjima qil: ...'*):",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_translate_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_translate_text(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Tarjima qilinmoqda...*", parse_mode="Markdown")

    result = await ai_service.translate_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 6. 📋 Reja tuzish
@router.callback_query(F.data == "text_plan")
async def cb_text_plan(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_plan_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="📋 **Reja tuzish**\n\nQaysi maqsad yoki loyiha uchun bosqichma-bosqich reja kerak? Yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_plan_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_plan_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Batafsil reja tuzilmoqda...*", parse_mode="Markdown")

    result = await ai_service.create_plan(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 7. 💼 Rasmiy matn
@router.callback_query(F.data == "text_formal")
async def cb_text_formal(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_formal_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="💼 **Rasmiy matn tuzish**\n\nAriza, rasmiy xat yoki taklifnoma haqida ma'lumot yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_formal_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_formal_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Rasmiy matn tayyorlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.formal_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# 8. 📱 Ijtimoiy tarmoq uchun post
@router.callback_query(F.data == "text_social")
async def cb_text_social(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TextStates.waiting_for_social_topic)
    await callback.message.delete()
    await callback.message.answer(
        text="📱 **Ijtimoiy tarmoq uchun matn**\n\nQaysi tarmoq (Telegram, Instagram va h.k.) va qanday mavzuda post kerak?",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(TextStates.waiting_for_social_topic, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_social_topic(message: Message, state: FSMContext, db_user: User, db_session: AsyncSession) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Post tayyorlanmoqda...*", parse_mode="Markdown")

    result = await ai_service.social_media_text(message.text, user_id=db_user.id, session=db_session)
    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()
