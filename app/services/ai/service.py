import base64
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.models.ai_usage import AIUsage
from app.database.models.conversation import Conversation
from app.database.models.message import Message
from app.services.ai.client import get_openai_client
from app.services.ai.prompts import (
    CHAT_SYSTEM_PROMPT,
    CHECK_KNOWLEDGE_PROMPT,
    CODING_ASSISTANT_PROMPT,
    CREATE_QUIZ_PROMPT,
    DECISION_BATTLE_PROMPT,
    DECISION_SYSTEM_PROMPT,
    EXPLAIN_TOPIC_PROMPT,
    IDEA_SYSTEM_PROMPT,
    LESSON_PLAN_PROMPT,
    MAKE_ME_LAUGH_PROMPT,
    MYSTERY_TASK_PROMPT,
    PERSONALITY_ANALYSIS_PROMPT,
    PROBLEM_ANALYSIS_PROMPT,
    QA_EDUCATION_PROMPT,
    RANDOM_CHALLENGE_PROMPT,
    ROAST_ME_PROMPT,
    TEXT_FORMAL_PROMPT,
    TEXT_IMPROVER_PROMPT,
    TEXT_PLAN_PROMPT,
    TEXT_REWRITER_PROMPT,
    TEXT_SOCIAL_MEDIA_PROMPT,
    TEXT_SUMMARIZER_PROMPT,
    TEXT_TRANSLATOR_PROMPT,
    TEXT_WRITER_PROMPT,
    THOUGHT_ANALYSIS_PROMPT,
    VISION_ANALYZE_PROMPT,
    VISION_OCR_PROMPT,
    VISION_QA_PROMPT,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
settings = get_settings()

AI_ERROR_USER_MESSAGE = (
    "⚠️ Hozircha sun’iy intellekt xizmatida muammo yuz berdi. Birozdan keyin qayta urinib ko‘ring."
)


class AIService:
    """
    OpenAI bilan barcha sun'iy intellekt amallarini bajaruvchi,
    tokenlar hisobini yurituvchi va xatoliklarni xavfsiz boshqaruvchi servis.
    """

    def __init__(self) -> None:
        self.client = get_openai_client()

    async def _record_usage(
        self,
        session: Optional[AsyncSession],
        user_id: int,
        feature: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        if not session or user_id <= 0:
            return
        try:
            usage = AIUsage(
                user_id=user_id,
                feature=feature,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            session.add(usage)
            await session.commit()
        except Exception as e:
            logger.error(f"AIUsage yozishda xatolik: {e}")
            await session.rollback()

    async def _generate_completion(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
        feature_name: str,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
        model: Optional[str] = None,
    ) -> str:
        used_model = model or settings.OPENAI_MODEL
        try:
            response = await self.client.chat.completions.create(
                model=used_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            content = response.choices[0].message.content or ""
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0

            await self._record_usage(
                session=session,
                user_id=user_id,
                feature=feature_name,
                model=used_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            return content.strip()
        except Exception as e:
            logger.error(f"OpenAI xatosi ({feature_name}): {e}", exc_info=True)
            return AI_ERROR_USER_MESSAGE

    # 1. 🧠 AI Chat (suhbat tarixi bilan)
    async def chat(
        self,
        user_message: str,
        user_id: int,
        session: AsyncSession,
        max_history: int = 10,
    ) -> str:
        try:
            # Userning oxirgi suhbatini topamiz yoki yaratamiz
            stmt = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            conv = result.scalar_one_or_none()

            if not conv:
                conv = Conversation(user_id=user_id, title="Yangi suhbat")
                session.add(conv)
                await session.flush()

            # Oxirgi N ta xabarni olamiz
            msg_stmt = (
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(max_history)
            )
            msg_result = await session.execute(msg_stmt)
            history_msgs = list(reversed(msg_result.scalars().all()))

            messages_payload: List[Dict[str, str]] = [
                {"role": "system", "content": CHAT_SYSTEM_PROMPT}
            ]
            for m in history_msgs:
                messages_payload.append({"role": m.role, "content": m.content})

            messages_payload.append({"role": "user", "content": user_message})

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages_payload,  # type: ignore
                max_tokens=settings.CHAT_MAX_TOKENS,
                temperature=0.7,
            )

            assistant_reply = (response.choices[0].message.content or "").strip()
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0

            # DB ga yozamiz
            session.add(Message(conversation_id=conv.id, role="user", content=user_message))
            session.add(Message(conversation_id=conv.id, role="assistant", content=assistant_reply))
            await session.commit()

            await self._record_usage(
                session=session,
                user_id=user_id,
                feature="ai_chat",
                model=settings.OPENAI_MODEL,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            return assistant_reply
        except Exception as e:
            logger.error(f"Chat amali xatosi: {e}", exc_info=True)
            return AI_ERROR_USER_MESSAGE

    async def clear_chat_history(self, user_id: int, session: AsyncSession) -> bool:
        """Foydalanuvchining yangi suhbat boshlashi uchun tarixni yangilash"""
        try:
            conv = Conversation(user_id=user_id, title="Yangi suhbat")
            session.add(conv)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Suhbat tarixini tozalashda xato: {e}")
            await session.rollback()
            return False

    # 🧠 Sun'iy intellekt bo'limi metodlari
    async def generate_idea(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=IDEA_SYSTEM_PROMPT,
            user_message=prompt,
            max_tokens=settings.CHAT_MAX_TOKENS,
            feature_name="generate_idea",
            user_id=user_id,
            session=session,
        )

    async def make_decision(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=DECISION_SYSTEM_PROMPT,
            user_message=prompt,
            max_tokens=settings.DECISION_MAX_TOKENS,
            feature_name="make_decision",
            user_id=user_id,
            session=session,
        )

    async def analyze_thought(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=THOUGHT_ANALYSIS_PROMPT,
            user_message=prompt,
            max_tokens=settings.CHAT_MAX_TOKENS,
            feature_name="analyze_thought",
            user_id=user_id,
            session=session,
        )

    async def analyze_problem(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=PROBLEM_ANALYSIS_PROMPT,
            user_message=prompt,
            max_tokens=settings.CHAT_MAX_TOKENS,
            feature_name="analyze_problem",
            user_id=user_id,
            session=session,
        )

    async def coding_assistant(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=CODING_ASSISTANT_PROMPT,
            user_message=prompt,
            max_tokens=settings.CODE_MAX_TOKENS,
            feature_name="coding_assistant",
            user_id=user_id,
            session=session,
        )

    # ✍️ Matn bilan ishlash
    async def write_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_WRITER_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="write_text",
            user_id=user_id,
            session=session,
        )

    async def improve_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_IMPROVER_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="improve_text",
            user_id=user_id,
            session=session,
        )

    async def summarize_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_SUMMARIZER_PROMPT,
            user_message=prompt,
            max_tokens=settings.SUMMARY_MAX_TOKENS,
            feature_name="summarize_text",
            user_id=user_id,
            session=session,
        )

    async def rewrite_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_REWRITER_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="rewrite_text",
            user_id=user_id,
            session=session,
        )

    async def translate_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_TRANSLATOR_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="translate_text",
            user_id=user_id,
            session=session,
        )

    async def create_plan(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_PLAN_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="create_plan",
            user_id=user_id,
            session=session,
        )

    async def formal_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_FORMAL_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="formal_text",
            user_id=user_id,
            session=session,
        )

    async def social_media_text(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=TEXT_SOCIAL_MEDIA_PROMPT,
            user_message=prompt,
            max_tokens=settings.WRITER_MAX_TOKENS,
            feature_name="social_media_text",
            user_id=user_id,
            session=session,
        )

    # 📚 Ta'lim
    async def explain_topic(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=EXPLAIN_TOPIC_PROMPT,
            user_message=prompt,
            max_tokens=settings.EDUCATION_MAX_TOKENS,
            feature_name="explain_topic",
            user_id=user_id,
            session=session,
        )

    async def create_quiz(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=CREATE_QUIZ_PROMPT,
            user_message=prompt,
            max_tokens=settings.EDUCATION_MAX_TOKENS,
            feature_name="create_quiz",
            user_id=user_id,
            session=session,
        )

    async def qa_education(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=QA_EDUCATION_PROMPT,
            user_message=prompt,
            max_tokens=settings.EDUCATION_MAX_TOKENS,
            feature_name="qa_education",
            user_id=user_id,
            session=session,
        )

    async def lesson_plan(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=LESSON_PLAN_PROMPT,
            user_message=prompt,
            max_tokens=settings.EDUCATION_MAX_TOKENS,
            feature_name="lesson_plan",
            user_id=user_id,
            session=session,
        )

    async def check_knowledge(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=CHECK_KNOWLEDGE_PROMPT,
            user_message=prompt,
            max_tokens=settings.EDUCATION_MAX_TOKENS,
            feature_name="check_knowledge",
            user_id=user_id,
            session=session,
        )

    # 🎮 Ko'ngilochar
    async def make_me_laugh(self, prompt: str = "Meni kuldiradigan hazil ayt", user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=MAKE_ME_LAUGH_PROMPT,
            user_message=prompt,
            max_tokens=settings.ENTERTAINMENT_MAX_TOKENS,
            feature_name="make_me_laugh",
            user_id=user_id,
            session=session,
        )

    async def roast_me(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=ROAST_ME_PROMPT,
            user_message=prompt,
            max_tokens=settings.ENTERTAINMENT_MAX_TOKENS,
            feature_name="roast_me",
            user_id=user_id,
            session=session,
        )

    async def analyze_personality(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=PERSONALITY_ANALYSIS_PROMPT,
            user_message=prompt,
            max_tokens=settings.ENTERTAINMENT_MAX_TOKENS,
            feature_name="analyze_personality",
            user_id=user_id,
            session=session,
        )

    async def generate_challenge(self, prompt: str = "Menga bugungi topshiriqni ber", user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=RANDOM_CHALLENGE_PROMPT,
            user_message=prompt,
            max_tokens=settings.ENTERTAINMENT_MAX_TOKENS,
            feature_name="random_challenge",
            user_id=user_id,
            session=session,
        )

    async def mystery_task(self, prompt: str = "Menga sirli vazifa yoki jumboq ber", user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=MYSTERY_TASK_PROMPT,
            user_message=prompt,
            max_tokens=settings.ENTERTAINMENT_MAX_TOKENS,
            feature_name="mystery_task",
            user_id=user_id,
            session=session,
        )

    async def decision_battle(self, prompt: str, user_id: int = 0, session: Optional[AsyncSession] = None) -> str:
        return await self._generate_completion(
            system_prompt=DECISION_BATTLE_PROMPT,
            user_message=prompt,
            max_tokens=settings.ENTERTAINMENT_MAX_TOKENS,
            feature_name="decision_battle",
            user_id=user_id,
            session=session,
        )

    # 📸 Vision (Rasm bilan ishlash)
    async def analyze_image(
        self,
        image_bytes: bytes,
        mode: str = "analyze",  # analyze, ocr, qa
        question: Optional[str] = None,
        user_id: int = 0,
        session: Optional[AsyncSession] = None,
    ) -> str:
        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            data_url = f"data:image/jpeg;base64,{b64_image}"

            if mode == "ocr":
                system_prompt = VISION_OCR_PROMPT
                user_text = "Rasmdagi barcha matnlarni aniqlang va yozib bering."
            elif mode == "qa":
                system_prompt = VISION_QA_PROMPT
                user_text = question or "Rasm bo‘yicha to‘liq ma'lumot bering."
            else:
                system_prompt = VISION_ANALYZE_PROMPT
                user_text = question or "Ushbu rasmni batafsil tahlil qilib bering."

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_text},
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url, "detail": "auto"},
                            },
                        ],
                    },
                ],
                max_tokens=settings.SUMMARY_MAX_TOKENS,
            )
            content = response.choices[0].message.content or ""
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0

            await self._record_usage(
                session=session,
                user_id=user_id,
                feature=f"vision_{mode}",
                model=settings.OPENAI_VISION_MODEL,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            return content.strip()
        except Exception as e:
            logger.error(f"Vision xatosi ({mode}): {e}", exc_info=True)
            return AI_ERROR_USER_MESSAGE
