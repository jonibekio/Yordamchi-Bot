import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.services.notes.note_service import NoteService


@pytest.mark.asyncio
async def test_notes_crud(db_session: AsyncSession, sample_user: User):
    # 1. Create
    note = await NoteService.create_note(
        session=db_session,
        user_id=sample_user.id,
        title="Kitoblar ro‘yxati",
        content="1. Atom Odatlar\n2. Alximik",
    )
    assert note.id is not None
    assert note.title == "Kitoblar ro‘yxati"

    # 2. Get list
    notes = await NoteService.get_user_notes(session=db_session, user_id=sample_user.id)
    assert len(notes) == 1
    assert notes[0].id == note.id

    # 3. Search
    found = await NoteService.search_notes(session=db_session, user_id=sample_user.id, query="Atom")
    assert len(found) == 1

    not_found = await NoteService.search_notes(session=db_session, user_id=sample_user.id, query="Matematika")
    assert len(not_found) == 0

    # 4. User isolation (boshqa user bu qaydni ko'rmasligi kerak)
    other_notes = await NoteService.get_user_notes(session=db_session, user_id=99999)
    assert len(other_notes) == 0

    # 5. Delete
    deleted = await NoteService.delete_note(session=db_session, user_id=sample_user.id, note_id=note.id)
    assert deleted is True

    notes_after_delete = await NoteService.get_user_notes(session=db_session, user_id=sample_user.id)
    assert len(notes_after_delete) == 0
