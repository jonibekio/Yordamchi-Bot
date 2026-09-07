from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import get_note_item_keyboard, get_notes_menu_keyboard
from app.bot.keyboards.reply import BTN_BACK, BTN_MAIN_MENU, get_back_keyboard
from app.bot.states.states import NoteStates
from app.database.models.user import User
from app.services.notes.note_service import NoteService
from app.utils.message_splitter import split_text

router = Router(name="notes")


# 1. ➕ Yangi qayd yaratish
@router.callback_query(F.data == "note_new")
async def cb_note_new(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NoteStates.waiting_for_title)
    await callback.message.delete()
    await callback.message.answer(
        text="📝 **Yangi qayd yaratish**\n\nQayd uchun sarlavha kiriting:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(NoteStates.waiting_for_title, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_note_title(message: Message, state: FSMContext) -> None:
    await state.update_data(note_title=message.text)
    await state.set_state(NoteStates.waiting_for_content)
    await message.answer(
        text="✍️ Endi qayd mazmunini (matnini) yozing:",
        reply_markup=get_back_keyboard(),
    )


@router.message(NoteStates.waiting_for_content, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_note_content(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    data = await state.get_data()
    title = data.get("note_title", "Nomsiz qayd")
    content = message.text

    note = await NoteService.create_note(
        session=db_session,
        user_id=db_user.id,
        title=title,
        content=content,
    )

    await state.clear()
    await message.answer(
        text=f"✅ **Qayd muvaffaqiyatli saqlandi!**\n\n📌 **{note.title}**\n{note.content}",
        reply_markup=get_notes_menu_keyboard(),
        parse_mode="Markdown",
    )


# 2. 📋 Qaydlar ro'yxati
@router.callback_query(F.data == "note_list")
async def cb_note_list(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    notes = await NoteService.get_user_notes(session=db_session, user_id=db_user.id)
    await callback.message.delete()

    if not notes:
        await callback.message.answer(
            text="📭 Sizda hozircha hech qanday qaydlar mavjud emas.",
            reply_markup=get_notes_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.answer("📋 **Sizning qaydlaringiz:**", parse_mode="Markdown")
    for note in notes:
        text = f"📌 **{note.title}**\n\n{note.content}\n\n🗓 *{note.created_at.strftime('%d.%m.%Y %H:%M')}*"
        await callback.message.answer(
            text=text,
            reply_markup=get_note_item_keyboard(note.id),
            parse_mode="Markdown",
        )
    await callback.answer()


# 3. 🔍 Qidirish
@router.callback_query(F.data == "note_search")
async def cb_note_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NoteStates.waiting_for_search_query)
    await callback.message.delete()
    await callback.message.answer(
        text="🔍 **Qaydlarni qidirish**\n\nQidirilayotgan kalit so‘zni yozing:",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(NoteStates.waiting_for_search_query, ~F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_note_search(
    message: Message,
    state: FSMContext,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    query = message.text
    notes = await NoteService.search_notes(session=db_session, user_id=db_user.id, query=query)

    if not notes:
        await message.answer(
            f"🔍 «{query}» bo‘yicha hech qanday qayd topilmadi.",
            reply_markup=get_notes_menu_keyboard(),
        )
        await state.clear()
        return

    await message.answer(f"🔍 **Topilgan qaydlar ({len(notes)} ta):**", parse_mode="Markdown")
    for note in notes:
        text = f"📌 **{note.title}**\n\n{note.content}\n\n🗓 *{note.created_at.strftime('%d.%m.%Y %H:%M')}*"
        await message.answer(
            text=text,
            reply_markup=get_note_item_keyboard(note.id),
            parse_mode="Markdown",
        )
    await state.clear()


# 4. 🗑 Qaydni o'chirish
@router.callback_query(F.data.startswith("note_del_"))
async def cb_note_delete(
    callback: CallbackQuery,
    db_user: User,
    db_session: AsyncSession,
) -> None:
    note_id = int(callback.data.split("_")[-1])
    success = await NoteService.delete_note(session=db_session, user_id=db_user.id, note_id=note_id)

    if success:
        await callback.message.delete()
        await callback.message.answer("🗑 Qayd muvaffaqiyatli o‘chirildi.")
    else:
        await callback.answer("⚠️ Qayd topilmadi yoki allaqachon o‘chirilgan.", show_alert=True)
    await callback.answer()
