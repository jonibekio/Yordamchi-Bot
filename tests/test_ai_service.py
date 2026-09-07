from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.ai_usage import AIUsage
from app.database.models.user import User
from app.services.ai.service import AIService


@pytest.mark.asyncio
async def test_ai_service_chat_and_usage(
    db_session: AsyncSession,
    sample_user: User,
    mock_openai_response,
):
    ai_service = AIService()

    with patch.object(ai_service.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_openai_response

        reply = await ai_service.chat(
            user_message="Salom, menga yordam bera olasizmi?",
            user_id=sample_user.id,
            session=db_session,
        )

        assert "Bu sun’iy intellekt tomonidan qaytarilgan o‘zbekcha javob." in reply
        mock_create.assert_awaited_once()

        # AIUsage bazaga yozilganligini tekshirish
        stmt = select(AIUsage).where(AIUsage.user_id == sample_user.id)
        res = await db_session.execute(stmt)
        usage = res.scalar_one_or_none()
        assert usage is not None
        assert usage.feature == "ai_chat"
        assert usage.input_tokens == 25
        assert usage.output_tokens == 40


@pytest.mark.asyncio
async def test_ai_service_decision_maker(
    db_session: AsyncSession,
    sample_user: User,
    mock_openai_response,
):
    ai_service = AIService()

    with patch.object(ai_service.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_openai_response

        reply = await ai_service.make_decision(
            prompt="Universitetda qolish yoki ishlash",
            user_id=sample_user.id,
            session=db_session,
        )

        assert reply != ""
        mock_create.assert_awaited_once()
