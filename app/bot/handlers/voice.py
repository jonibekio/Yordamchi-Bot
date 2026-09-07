import io
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import VoiceStates
from app.database.models.user import User
from app.services.speech.speech_service import SpeechService
from app.utils.message_splitter import split_text

router = Router(name="voice")
speech_service = SpeechService()


# 1. 📝 Ovozdan matnga (STT) - menyu tugmasi
@router.callback_query(F.data == "voice_stt")
async def cb_voice_stt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VoiceStates.waiting_for_voice)
    await callback.message.delete()
    await callback.message.answer(
        text="🎙 **Ovozni matnga aylantirish**\n\nIltimos, Telegram orqali ovozli xabar (voice message) yuboring:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# 2. 🗣 Matndan ovozga (TTS) - menyu tugmasi
@router.callback_query(F.data == "voice_tts")
async def cb_voice_tts(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(VoiceStates.waiting_for_tts_text)
    await callback.message.delete()
    await callback.message.answer(
        text="🗣 **Matnni ovozga aylantirish (TTS)**\n\nOvozga aylantirmoqchi bo‘lgan matningizni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


# TTS matnini qabul qilish
@router.message(VoiceStates.waiting_for_tts_text, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_tts_text(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.RECORD_VOICE)
    status_msg = await message.answer("⏳ *Ovoz yozilmoqda...*", parse_mode="Markdown")

    audio_bytes = await speech_service.text_to_speech(
        text=message.text,
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    if audio_bytes:
        voice_file = BufferedInputFile(audio_bytes, filename="voice.mp3")
        await message.answer_voice(voice=voice_file, caption="🗣 Matningiz ovozga aylantirildi.")
    else:
        await message.answer("⚠️ Matnni ovozga aylantirishda xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")
    await state.clear()


# Telegram ovozli xabarini qabul qilish (istalgan vaqtda yoki state ichida)
@router.message(F.voice)
async def handle_incoming_voice(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    status_msg = await message.answer("⏳ *Ovozli xabar matnga aylantirilmoqda...*", parse_mode="Markdown")

    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    file_bytes_io = io.BytesIO()
    await message.bot.download_file(file.file_path, file_bytes_io)
    audio_bytes = file_bytes_io.getvalue()

    text = await speech_service.speech_to_text(
        audio_bytes=audio_bytes,
        filename="voice.ogg",
        user_id=db_user.id,
        session=db_session,
    )

    await status_msg.delete()
    response_header = "🎙 **Ovozdan olingan matn:**\n\n"
    full_response = f"{response_header}«{text}»"

    for chunk in split_text(full_response):
        await message.answer(chunk, parse_mode="Markdown")

    await state.clear()
