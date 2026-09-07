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

    # OpenAI
    OPENAI_API_KEY: str = Field(default="mock_key", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="Asosiy chat modeli")
    OPENAI_VISION_MODEL: str = Field(default="gpt-4o", description="Rasm tahlili modeli")
    OPENAI_WHISPER_MODEL: str = Field(default="whisper-1", description="Ovozni matnga o'girish modeli")
    OPENAI_TTS_MODEL: str = Field(default="tts-1", description="Matnni ovozga o'girish modeli")
    OPENAI_TTS_VOICE: str = Field(default="alloy", description="TTS ovoz tembri")

    # Database & Redis
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_bot_db",
        description="Async PostgreSQL ulanish satri",
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis ulanish satri",
    )

    # Token limits (Cost Control)
    CHAT_MAX_TOKENS: int = 1000
    SUMMARY_MAX_TOKENS: int = 1500
    WRITER_MAX_TOKENS: int = 2000
    DECISION_MAX_TOKENS: int = 1500
    CODE_MAX_TOKENS: int = 2000
    EDUCATION_MAX_TOKENS: int = 1500
    ENTERTAINMENT_MAX_TOKENS: int = 1000

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 20
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
