import io
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import get_pdf_actions_keyboard
from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import DocumentStates
from app.config.settings import get_settings
from app.database.models.user import User
from app.services.documents.pdf_service import PDFService
from app.utils.message_splitter import split_text

router = Router(name="documents")
pdf_service = PDFService()
settings = get_settings()


@router.message(F.document)
async def handle_incoming_document(
    message: Message,
    state: FSMContext,
) -> None:
    doc = message.document
    if not doc or not doc.file_name or not doc.file_name.lower().endswith(".pdf"):
        await message.answer("⚠️ Iltimos, faqat **PDF** formatidagi hujjat yuboring.")
        return

    # Hajm tekshiruvi
    file_size_mb = (doc.file_size or 0) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        await message.answer(
            f"⚠️ Hujjat hajmi juda katta ({file_size_mb:.1f} MB). "
            f"Maksimal {settings.MAX_FILE_SIZE_MB} MB gacha ruxsat berilgan."
        )
        return

    status_msg = await message.answer("⏳ *PDF hujjati o‘qilmoqda va matn ajratilmoqda...*", parse_mode="Markdown")

    file = await message.bot.get_file(doc.file_id)
    file_bytes_io = io.BytesIO()
    await message.bot.download_file(file.file_path, file_bytes_io)
    pdf_bytes = file_bytes_io.getvalue()

    success, result_text = pdf_service.extract_text(pdf_bytes)
    await status_msg.delete()

    if not success:
        await message.answer(result_text)
        return

    # FSM da saqlab turamiz
    await state.update_data(pdf_text=result_text, pdf_name=doc.file_name)

    await message.answer(
        text=f"📄 **Hujjat qabul qilindi:** «{doc.file_name}»\n\nQuyidagi amallardan birini tanlang:",
        reply_markup=get_pdf_actions_keyboard(),
        parse_mode="Markdown",
    )


# 1. 📖 Qisqartirish
@router.callback_query(F.data == "pdf_summarize")
async def cb_pdf_summarize(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    data = await state.get_data()
    pdf_text = data.get("pdf_text")
    if not pdf_text:
        await callback.answer("⚠️ Hujjat topilmadi. Qaytadan PDF yuboring.", show_alert=True)
        return

    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ *Hujjat umumlashtirilmoqda va qisqartirilmoqda...*", parse_mode="Markdown")

    summary = await pdf_service.summarize_document(
        document_text=pdf_text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(f"📖 **Hujjat xulosasi:**\n\n{summary}"):
        await callback.message.answer(chunk, parse_mode="Markdown")
    await callback.answer()


# 2. 📊 Tahlil qilish
@router.callback_query(F.data == "pdf_analyze")
async def cb_pdf_analyze(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    data = await state.get_data()
    pdf_text = data.get("pdf_text")
    if not pdf_text:
        await callback.answer("⚠️ Hujjat topilmadi. Qaytadan PDF yuboring.", show_alert=True)
        return

    await callback.message.delete()
    status_msg = await callback.message.answer("⏳ *Hujjat har tomonlama chuqur tahlil qilinmoqda...*", parse_mode="Markdown")

    analysis = await pdf_service.analyze_document(
        document_text=pdf_text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(f"📊 **Hujjat tahlili:**\n\n{analysis}"):
        await callback.message.answer(chunk, parse_mode="Markdown")
    await callback.answer()


# 3. 🔍 Ma'lumot topish
@router.callback_query(F.data == "pdf_search")
async def cb_pdf_search(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("pdf_text"):
        await callback.answer("⚠️ Hujjat topilmadi. Qaytadan PDF yuboring.", show_alert=True)
        return

    await state.set_state(DocumentStates.waiting_for_pdf_search)
    await callback.message.delete()
    await callback.message.answer(
        text="🔍 **Hujjatdan ma'lumot izlash**\n\nHujjat ichidan qanday ma'lumot yoki javob qidiryapsiz? Yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(DocumentStates.waiting_for_pdf_search, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_pdf_search_query(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    data = await state.get_data()
    pdf_text = data.get("pdf_text")
    if not pdf_text:
        await message.answer("⚠️ Hujjat topilmadi. Iltimos, yangitdan PDF yuboring.")
        await state.clear()
        return

    status_msg = await message.answer("⏳ *Hujjat ichidan ma'lumot qidirilmoqda...*", parse_mode="Markdown")

    res = await pdf_service.find_information(
        document_text=pdf_text,
        query=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(res):
        await message.answer(chunk)


# 4. ❓ Savol berish
@router.callback_query(F.data == "pdf_qa")
async def cb_pdf_qa(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("pdf_text"):
        await callback.answer("⚠️ Hujjat topilmadi. Qaytadan PDF yuboring.", show_alert=True)
        return

    await state.set_state(DocumentStates.waiting_for_pdf_qa)
    await callback.message.delete()
    await callback.message.answer(
        text="❓ **Hujjat bo‘yicha savol berish**\n\nHujjatga oid savolingizni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(DocumentStates.waiting_for_pdf_qa, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_pdf_qa_query(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    data = await state.get_data()
    pdf_text = data.get("pdf_text")
    if not pdf_text:
        await message.answer("⚠️ Hujjat topilmadi. Iltimos, yangitdan PDF yuboring.")
        await state.clear()
        return

    status_msg = await message.answer("⏳ *Savolga javob tayyorlanmoqda...*", parse_mode="Markdown")

    res = await pdf_service.ask_question(
        document_text=pdf_text,
        question=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    for chunk in split_text(res):
        await message.answer(chunk)
