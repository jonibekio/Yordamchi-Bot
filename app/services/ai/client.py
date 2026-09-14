from typing import Optional
from openai import AsyncOpenAI
from app.config.settings import get_settings

settings = get_settings()
_ai_client: Optional[AsyncOpenAI] = None


def is_gemini_active() -> bool:
    """Gemini API kaliti mavjudligini tekshirish"""
    key = settings.GEMINI_API_KEY.strip()
    return bool(key and not key.startswith("bu_yerga") and key != "mock_key")


def get_active_model() -> str:
    """Hozirda faol model nomini qaytaradi"""
    if is_gemini_active():
        return settings.GEMINI_MODEL
    return settings.OPENAI_MODEL


def get_active_vision_model() -> str:
    """Rasm tahlili uchun faol model nomini qaytaradi"""
    if is_gemini_active():
        return settings.GEMINI_MODEL
    return settings.OPENAI_VISION_MODEL


def get_openai_client() -> AsyncOpenAI:
    global _ai_client
    if _ai_client is None:
        if is_gemini_active():
            _ai_client = AsyncOpenAI(
                api_key=settings.GEMINI_API_KEY,
                base_url=settings.GEMINI_BASE_URL,
            )
        else:
            api_key = settings.OPENAI_API_KEY or "mock_key"
            _ai_client = AsyncOpenAI(api_key=api_key)
    return _ai_client
