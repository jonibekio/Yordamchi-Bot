from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.documents.pdf_service import PDFService
from app.services.speech.speech_service import SpeechService


@pytest.mark.asyncio
async def test_speech_service_stt_and_tts(db_session, sample_user):
    speech_service = SpeechService()

    # 1. Mock Whisper STT (is_gemini_active=False bo'lganda)
    mock_transcription = MagicMock()
    mock_transcription.text = "Bugun soat beshda uchrashuvim bor."

    with patch("app.services.speech.speech_service.is_gemini_active", return_value=False):
        with patch.object(speech_service.client.audio.transcriptions, "create", new_callable=AsyncMock) as mock_stt:
            mock_stt.return_value = mock_transcription

            result_text = await speech_service.speech_to_text(
                audio_bytes=b"fake_audio_bytes",
                filename="test.ogg",
                user_id=sample_user.id,
                session=db_session,
            )

            assert "Bugun soat beshda uchrashuvim bor." in result_text
            mock_stt.assert_awaited_once()

    # 2. Mock Edge TTS
    mock_communicate = MagicMock()
    async def mock_stream():
        yield {"type": "audio", "data": b"fake_mp3_bytes"}
    mock_communicate.stream = mock_stream

    with patch("edge_tts.Communicate", return_value=mock_communicate):
        audio_res = await speech_service.text_to_speech(
            text="Assalomu alaykum",
            user_id=sample_user.id,
            session=db_session,
        )

        assert audio_res == b"fake_mp3_bytes"


@pytest.mark.asyncio
async def test_pdf_service_page_limit_and_error():
    pdf_service = PDFService()

    # Invalid PDF bytes test
    success, error_msg = pdf_service.extract_text(b"corrupted_bytes")
    assert success is False
    assert "xatolik yuz berdi" in error_msg
