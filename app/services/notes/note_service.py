from typing import List, Optional
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.note import Note
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class NoteService:
    @staticmethod
    async def create_note(
        session: AsyncSession,
        user_id: int,
        title: str,
        content: str,
    ) -> Note:
        note = Note(
            user_id=user_id,
            title=title.strip(),
            content=content.strip(),
        )
        session.add(note)
        await session.commit()
        await session.refresh(note)
        return note

    @staticmethod
    async def get_user_notes(
        session: AsyncSession,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Note]:
        stmt = (
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(desc(Note.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_note_by_id(
        session: AsyncSession,
        user_id: int,
        note_id: int,
    ) -> Optional[Note]:
        stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def search_notes(
        session: AsyncSession,
        user_id: int,
        query: str,
    ) -> List[Note]:
        pattern = f"%{query}%"
        stmt = (
            select(Note)
            .where(
                Note.user_id == user_id,
                (Note.title.ilike(pattern)) | (Note.content.ilike(pattern)),
            )
            .order_by(desc(Note.created_at))
            .limit(20)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_note(
        session: AsyncSession,
        user_id: int,
        note_id: int,
    ) -> bool:
        stmt = delete(Note).where(Note.id == note_id, Note.user_id == user_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
