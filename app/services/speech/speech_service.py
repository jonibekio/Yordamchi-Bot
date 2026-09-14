import asyncio
import io
import os
import tempfile
from typing import Optional
import edge_tts
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.models.ai_usage import AIUsage
from app.services.ai.client import get_active_model, get_openai_client, is_gemini_active
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


class SpeechService:
    def __init__(self) -> None:
        self.client = get_openai_client()

    async def speech_to_text(
        self,
        audio_bytes: bytes,
        filename: str = "voice.ogg",
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> str:
        """
        Ovozli xabarni matnga aylantirish.
        Gemini faol bo'lsa - Gemini multimodal orqali,
        aks holda OpenAI Whisper orqali bajariladi.
        """
        # 1. Agar Gemini faol bo'lsa, Gemini orqali o'giramiz
        if is_gemini_active():
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)

                mime_type = "audio/ogg" if filename.lower().endswith(".ogg") else "audio/mp3"
                prompt = (
                    "Ushbu audio xabardagi barcha so‘zlarni aynan o‘zbek tilida matnga aylantiring (transkripsiya qiling). "
                    "Hech qanday qo‘shimcha izoh, kirish yoki xulosa gap qo‘shmang, faqat aytilgan nutq matnini qaytaring."
                )

                response = await asyncio.to_thread(
                    model.generate_content,
                    [
                        {"mime_type": mime_type, "data": audio_bytes},
                        prompt,
                    ],
                )
                text = (response.text or "").strip()

                if session and user_id > 0:
                    try:
                        usage = AIUsage(
                            user_id=user_id,
                            feature="speech_to_text_gemini",
                            model=settings.GEMINI_MODEL,
                            input_tokens=0,
                            output_tokens=len(text.split()),
                        )
                        session.add(usage)
                        await session.commit()
                    except Exception as db_err:
                        logger.error(f"AIUsage yozishda xato: {db_err}")
                        await session.rollback()

                return text
            except Exception as gemini_err:
                logger.warning(f"Gemini orqali ovozni matnga aylantirishda xatolik: {gemini_err}. Whisper tekshiriladi.")

        # 2. OpenAI Whisper orqali
        temp_file_path = None
        try:
            suffix = os.path.splitext(filename)[1] or ".ogg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            with open(temp_file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model=settings.OPENAI_WHISPER_MODEL,
                    file=audio_file,
                )

            text = transcription.text.strip()

            if session and user_id > 0:
                try:
                    usage = AIUsage(
                        user_id=user_id,
                        feature="speech_to_text_whisper",
                        model=settings.OPENAI_WHISPER_MODEL,
                        input_tokens=0,
                        output_tokens=len(text.split()),
                    )
                    session.add(usage)
                    await session.commit()
                except Exception as db_err:
                    logger.error(f"AIUsage yozishda xato: {db_err}")
                    await session.rollback()

            return text
        except Exception as e:
            logger.error(f"Ovozni matnga aylantirishda xato: {e}", exc_info=True)
            return "⚠️ Ovozni matnga aylantirishda xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring."
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass

    async def text_to_speech(
        self,
        text: str,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> Optional[bytes]:
        """
        Matnni ovozga aylantirish.
        Edge TTS orqali tabiiy o'zbek ovozida (Madina/Sardor) yaratiladi.
        Zaxira sifatida OpenAI TTS ishlatiladi.
        """
        # 1. Edge TTS (O'zbek tili uchun bepul va eng sifatli)
        try:
            communicate = edge_tts.Communicate(text, settings.TTS_VOICE_UZBEK)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            if audio_data:
                if session and user_id > 0:
                    try:
                        usage = AIUsage(
                            user_id=user_id,
                            feature="text_to_speech_edge",
                            model=settings.TTS_VOICE_UZBEK,
                            input_tokens=len(text.split()),
                            output_tokens=0,
                        )
                        session.add(usage)
                        await session.commit()
                    except Exception as db_err:
                        logger.error(f"AIUsage yozishda xato: {db_err}")
                        await session.rollback()
                return audio_data
        except Exception as edge_err:
            logger.warning(f"Edge TTS xatosi: {edge_err}. OpenAI TTS sinab ko'riladi.")

        # 2. OpenAI TTS zaxirasi
        try:
            response = await self.client.audio.speech.create(
                model=settings.OPENAI_TTS_MODEL,
                voice=settings.OPENAI_TTS_VOICE,  # type: ignore
                input=text,
                response_format="mp3",
            )
            audio_bytes = response.content

            if session and user_id > 0:
                try:
                    usage = AIUsage(
                        user_id=user_id,
                        feature="text_to_speech_openai",
                        model=settings.OPENAI_TTS_MODEL,
                        input_tokens=len(text.split()),
                        output_tokens=0,
                    )
                    session.add(usage)
                    await session.commit()
                except Exception as db_err:
                    logger.error(f"AIUsage yozishda xato: {db_err}")
                    await session.rollback()

            return audio_bytes
        except Exception as e:
            logger.error(f"Matnni ovozga aylantirishda xato: {e}", exc_info=True)
            return None
