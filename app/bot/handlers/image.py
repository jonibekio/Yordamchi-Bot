import io
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import ImageStates
from app.database.models.user import User
from app.services.ai.service import AIService
from app.utils.message_splitter import split_text

router = Router(name="image")
ai_service = AIService()


def get_photo_actions_inline(file_id: str) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🔍 Rasmni tahlil qilish", callback_data=f"do_img_analyze:{file_id}")],
        [InlineKeyboardButton(text="📝 Matnni aniqlash (OCR)", callback_data=f"do_img_ocr:{file_id}")],
        [InlineKeyboardButton(text="❓ Rasm bo‘yicha savol berish", callback_data=f"do_img_qa:{file_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# Menyu orqali kirish
@router.callback_query(F.data == "img_analyze")
async def cb_img_analyze(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ImageStates.waiting_for_image)
    await state.update_data(image_mode="analyze")
    await callback.message.delete()
    await callback.message.answer(
        text="🔍 **Rasmni tahlil qilish**\n\nIltimos, tahlil qilish uchun rasm yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "img_ocr")
async def cb_img_ocr(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ImageStates.waiting_for_image)
    await state.update_data(image_mode="ocr")
    await callback.message.delete()
    await callback.message.answer(
        text="📝 **Rasmdagi matnni aniqlash (OCR)**\n\nIltimos, matni o‘qilishi kerak bo‘lgan rasmni yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "img_qa")
async def cb_img_qa(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ImageStates.waiting_for_image)
    await state.update_data(image_mode="qa")
    await callback.message.delete()
    await callback.message.answer(
        text="❓ **Rasm haqida savol berish**\n\nIltimos, avval rasmni yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# Rasm qabul qilish
@router.message(F.photo)
async def handle_incoming_photo(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    current_state = await state.get_state()
    state_data = await state.get_data()
    mode = state_data.get("image_mode")

    photo = message.photo[-1]  # Eng yuqori sifatli rasm
    file_id = photo.file_id

    # Agar foydalanuvchi ma'lum rejimda bo'lsa
    if current_state == ImageStates.waiting_for_image.state and mode:
        if mode == "qa":
            # Savol kutilmoqda
            await state.set_state(ImageStates.waiting_for_image_qa_question)
            await state.update_data(file_id=file_id)
            await message.answer(
                text="✅ Rasm qabul qilindi. Endi ushbu rasm bo‘yicha savolingizni yozing:",
                reply_markup=get_back_keyboard(),
            )
            return

        # analyze yoki ocr rejimi
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        status_msg = await message.answer("⏳ *Rasm sun’iy intellekt tomonidan tahlil qilinmoqda...*", parse_mode="Markdown")

        file = await message.bot.get_file(file_id)
        file_bytes_io = io.BytesIO()
        await message.bot.download_file(file.file_path, file_bytes_io)
        image_bytes = file_bytes_io.getvalue()

        result = await ai_service.analyze_image(
            image_bytes=image_bytes,
            mode=mode,
            user_id=db_user.id,
            session=db_session,
        )

        await status_msg.delete()
        for chunk in split_text(result):
            await message.answer(chunk)
        await state.clear()
        return

    # Foydalanuvchi shunchaki rasm yuborganda harakatlar menyusi chiqadi
    await message.answer(
        text="📸 Rasm qabul qilindi. Nima amal bajarmoqchisiz?",
        reply_markup=get_photo_actions_inline(file_id),
    )


# Rasm bo'yicha savol berish qadami
@router.message(ImageStates.waiting_for_image_qa_question, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_image_qa_question(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    data = await state.get_data()
    file_id = data.get("file_id")

    if not file_id:
        await message.answer("⚠️ Rasm topilmadi. Iltimos, qaytadan yuboring.")
        await state.clear()
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Rasm bo‘yicha savolga javob tayyorlanmoqda...*", parse_mode="Markdown")

    file = await message.bot.get_file(file_id)
    file_bytes_io = io.BytesIO()
    await message.bot.download_file(file.file_path, file_bytes_io)
    image_bytes = file_bytes_io.getvalue()

    result = await ai_service.analyze_image(
        image_bytes=image_bytes,
        mode="qa",
        question=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await message.answer(chunk)
    await state.clear()


# Shunchaki yuborilgan rasmdan so'ng inline tugma bosilganda
@router.callback_query(F.data.startswith("do_img_"))
async def handle_do_image_callback(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    action_data = callback.data.split(":", 1)
    action = action_data[0]
    file_id = action_data[1]

    if action == "do_img_qa":
        await state.set_state(ImageStates.waiting_for_image_qa_question)
        await state.update_data(file_id=file_id)
        await callback.message.delete()
        await callback.message.answer(
            text="❓ Ushbu rasm bo‘yicha qanday savolingiz bor? Savolingizni yozing:",
            reply_markup=get_back_keyboard(),
        )
        await callback.answer()
        return

    mode = "ocr" if action == "do_img_ocr" else "analyze"
    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ *Rasm tahlil qilinmoqda...*", parse_mode="Markdown")

    file = await callback.bot.get_file(file_id)
    file_bytes_io = io.BytesIO()
    await callback.bot.download_file(file.file_path, file_bytes_io)
    image_bytes = file_bytes_io.getvalue()

    result = await ai_service.analyze_image(
        image_bytes=image_bytes,
        mode=mode,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(result):
        await callback.message.answer(chunk)
    await callback.answer()
