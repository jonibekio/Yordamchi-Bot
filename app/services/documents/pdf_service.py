import io
from typing import Optional
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.services.ai.service import AIService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()


class PDFService:
    def __init__(self, ai_service: Optional[AIService] = None) -> None:
        self.ai_service = ai_service or AIService()

    def extract_text(self, pdf_bytes: bytes) -> tuple[bool, str]:
        """
        PDF baytlaridan matn ajratib olish va xavfsizlik cheklovlarini tekshirish.
        Returns: (success: bool, text_or_error: str)
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)

            if total_pages > settings.MAX_PDF_PAGES:
                return (
                    False,
                    f"⚠️ Hujjat hajmi juda katta! Maksimal {settings.MAX_PDF_PAGES} sahifagacha ruxsat berilgan. "
                    f"Sizning hujjatingizda {total_pages} sahifa bor.",
                )

            extracted_chunks = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_chunks.append(f"--- {idx + 1}-sahifa ---\n{page_text}")

            full_text = "\n\n".join(extracted_chunks).strip()

            if not full_text:
                return (
                    False,
                    "⚠️ Hujjatdan matn ajratib bo‘lmadi. Ehtimol bu skaner qilingan rasm yoki himoyalangan fayl.",
                )

            # Agar matn haddan tashqari uzun bo'lsa (masalan 40,000 belgi) qisqartirish
            max_chars = 30000
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + "\n\n[... Matn hajmi cheklovi tufayli qolgan qismi qisqartirildi ...]"

            return True, full_text
        except Exception as e:
            logger.error(f"PDF matn ajratishda xatolik: {e}", exc_info=True)
            return False, "⚠️ Hujjatni o‘qishda xatolik yuz berdi. Fayl buzilmaganligiga ishonch hosil qiling."

    async def summarize_document(
        self,
        document_text: str,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> str:
        prompt = (
            f"Quyidagi PDF hujjat matnini to‘liq tahlil qilib, uning eng asosiy mazmuni, "
            f"muhim nuqtalari va xulosalarini ixcham, tushunarli qilib bayon eting:\n\n{document_text}"
        )
        return await self.ai_service.summarize_text(prompt, user_id=user_id, session=session)

    async def find_information(
        self,
        document_text: str,
        query: str,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> str:
        prompt = (
            f"Foydalanuvchi quyidagi PDF hujjatidan ma'lumot izlamoqda.\n"
            f"Qidirilayotgan savol/mavzu: {query}\n\n"
            f"Hujjat matni:\n{document_text}\n\n"
            f"Iltimos, faqat ushbu hujjatdagi ma'lumotlarga tayangan holda aniq javob bering."
        )
        return await self.ai_service.explain_topic(prompt, user_id=user_id, session=session)

    async def ask_question(
        self,
        document_text: str,
        question: str,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> str:
        prompt = (
            f"Hujjat matni:\n{document_text}\n\n"
            f"Foydalanuvchi savoli: {question}\n\n"
            f"Ushbu savolga hujjat asosida o‘zbek tilida to‘liq va mantiqli javob bering."
        )
        return await self.ai_service.chat(prompt, user_id=user_id, session=session) if session else (
            await self.ai_service.explain_topic(prompt, user_id=user_id, session=session)
        )

    async def analyze_document(
        self,
        document_text: str,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> str:
        prompt = (
            f"Quyidagi hujjatni chuqur tahlil qiling: uning turi (maqola, shartnoma, hisobot va h.k.), "
            f"asosiy g‘oyalari, kuchli va zaif tomonlari, ahamiyati haqida batafsil tahliliy xulosa yozing:\n\n{document_text}"
        )
        return await self.ai_service.analyze_thought(prompt, user_id=user_id, session=session)
