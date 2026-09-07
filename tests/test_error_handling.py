from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.services.ai.service import AI_ERROR_USER_MESSAGE, AIService


@pytest.mark.asyncio
async def test_openai_api_error_graceful_handling(
    db_session: AsyncSession,
    sample_user: User,
):
    ai_service = AIService()

    # Simulating OpenAI API Error
    with patch.object(ai_service.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("OpenAI API ulanish uzildi (Simulated error)")

        reply = await ai_service.chat(
            user_message="Salom",
            user_id=sample_user.id,
            session=db_session,
        )

        # Foydalanuvchiga traceback emas, o'zbekcha chiroyli xabar qaytishi shart
        assert reply == AI_ERROR_USER_MESSAGE
        assert "traceback" not in reply.lower()
        assert "exception" not in reply.lower()
