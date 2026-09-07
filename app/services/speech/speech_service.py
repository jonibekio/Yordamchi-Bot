import io
import os
import tempfile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.models.ai_usage import AIUsage
from app.services.ai.client import get_openai_client
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
        Ovozli xabarni matnga aylantirish (Whisper).
        """
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

            # AIUsage hisobi
            if session and user_id > 0:
                try:
                    usage = AIUsage(
                        user_id=user_id,
                        feature="speech_to_text",
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
        Matnni ovozga aylantirish (OpenAI TTS).
        """
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
                        feature="text_to_speech",
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
