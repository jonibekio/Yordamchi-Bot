from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot
    BOT_TOKEN: str = Field(default="mock_token", description="Telegram bot API token")
    ADMIN_ID: int = Field(default=0, description="Telegram bot admin ID")

    # AI Provider ('gemini' yoki 'openai')
    AI_PROVIDER: str = Field(default="gemini", description="AI provayderi (gemini yoki openai)")

    # Google Gemini sozlamalari
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API kaliti")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash", description="Asosiy Gemini modeli")
    GEMINI_BASE_URL: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        description="Gemini OpenAI-compatible endpoint",
    )

    # OpenAI sozlamalari (Ixtiyoriy muqobil)
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="Asosiy chat modeli")
    OPENAI_VISION_MODEL: str = Field(default="gpt-4o", description="Rasm tahlili modeli")
    OPENAI_WHISPER_MODEL: str = Field(default="whisper-1", description="Ovozni matnga o'girish modeli")
    OPENAI_TTS_MODEL: str = Field(default="tts-1", description="Matnni ovozga o'girish modeli")
    OPENAI_TTS_VOICE: str = Field(default="alloy", description="TTS ovoz tembri")

    # O'zbekcha TTS (Edge TTS - bepul va yuqori sifatli)
    TTS_VOICE_UZBEK: str = Field(default="uz-UZ-MadinaNeural", description="O'zbekcha ovoz (Madina yoki Sardor)")

    # Database & Redis
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///bot.db",
        description="Ma'lumotlar bazasi ulanish satri (SQLite yoki PostgreSQL)",
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis ulanish satri",
    )

    # Token limits (Cost Control)
    CHAT_MAX_TOKENS: int = 1500
    SUMMARY_MAX_TOKENS: int = 2000
    WRITER_MAX_TOKENS: int = 2500
    DECISION_MAX_TOKENS: int = 2000
    CODE_MAX_TOKENS: int = 2500
    EDUCATION_MAX_TOKENS: int = 2000
    ENTERTAINMENT_MAX_TOKENS: int = 1500

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # File & Audio limits
    MAX_FILE_SIZE_MB: int = 20
    MAX_PDF_PAGES: int = 50

    # General
    DEFAULT_TIMEZONE: str = "Asia/Tashkent"
    DEBUG: bool = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
