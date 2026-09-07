from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.inline import (
    get_ai_menu_keyboard,
    get_education_menu_keyboard,
    get_entertainment_menu_keyboard,
    get_image_menu_keyboard,
    get_notes_menu_keyboard,
    get_pdf_actions_keyboard,
    get_reminders_menu_keyboard,
    get_settings_menu_keyboard,
    get_text_menu_keyboard,
    get_voice_menu_keyboard,
)
from app.bot.keyboards.reply import (
    BTN_AI,
    BTN_BACK,
    BTN_DOCS,
    BTN_EDUCATION,
    BTN_ENTERTAINMENT,
    BTN_IMAGE,
    BTN_MAIN_MENU,
    BTN_NOTES,
    BTN_REMINDERS,
    BTN_SETTINGS,
    BTN_STATS,
    BTN_TEXT,
    BTN_VOICE,
    get_back_keyboard,
    get_main_menu_keyboard,
)
from app.bot.states.states import DocumentStates

router = Router(name="start")

START_WELCOME_TEXT = (
    "🤖 **O‘zbek AI Yordamchi**\n\n"
    "Assalomu alaykum! Men sizga sun’iy intellekt yordamida matn, rasm, ovoz, "
    "hujjat, ta’lim va boshqa ko‘plab vazifalarda yordam beraman.\n\n"
    "Quyidagi bo‘limlardan birini tanlang 👇"
)

HELP_TEXT = (
    "📖 **Yordam va Bot bo‘yicha qo‘llanma**\n\n"
    "Bu bot 100% o‘zbek tilida ishlaydi va quyidagi imkoniyatlarga ega:\n\n"
    "🧠 **Sun’iy intellekt**: Suhbat, g‘oya, qaror qabul qilish, kod yozish va tahlil\n"
    "✍️ **Matn vositalari**: Matn yozish, yaxshilash, qisqartirish, tarjima, reja\n"
    "📸 **Rasm**: Rasmni tahlil qilish, OCR (matnni o‘qish), savol-javob\n"
    "🎙 **Ovoz**: Ovozli xabarni matnga (Whisper) va matnni ovozga aylantirish (TTS)\n"
    "📄 **Hujjat (PDF)**: PDF qisqartirish, ma'lumot izlash, savol-javob\n"
    "📚 **Ta’lim**: Mavzuni sodda tushuntirish, test tuzish, dars rejasi\n"
    "🎮 **Ko‘ngilochar**: Hazillar, tanqid (roast), xarakter tahlili, sirli vazifalar\n"
    "📝 **Qaydlar**: Shaxsiy eslatma va qaydlaringizni xavfsiz saqlash\n"
    "⏰ **Eslatmalar**: Kerakli vaqtda eslatma yuborish\n"
    "📊 **Faoliyatim**: Ishlatilgan tokenlar va shaxsiy statistikangiz\n\n"
    "Har doim **⬅️ Orqaga** yoki **🏠 Bosh menyu** tugmasi orqali qaytishingiz mumkin."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=START_WELCOME_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await message.answer(
        text=HELP_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


@router.message(F.text.in_({BTN_BACK, BTN_MAIN_MENU}))
async def handle_back_or_home(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="🏠 **Bosh menyu**\n\nQaysi bo‘limdan foydalanishni xohlaysiz?",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


# Asosiy bo'limlar ochilishi
@router.message(F.text == BTN_AI)
async def open_ai_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="🧠 **Sun’iy intellekt bo‘limi**\n\nKerakli yo‘nalishni tanlang:",
        reply_markup=get_ai_menu_keyboard(),
    )


@router.message(F.text == BTN_TEXT)
async def open_text_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="✍️ **Matn bilan ishlash bo‘limi**\n\nQanday matn amalini bajarmoqchisiz?",
        reply_markup=get_text_menu_keyboard(),
    )


@router.message(F.text == BTN_IMAGE)
async def open_image_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="📸 **Rasm bilan ishlash bo‘limi**\n\nRasmni yuboring yoki quyidagi amalni tanlang:",
        reply_markup=get_image_menu_keyboard(),
    )


@router.message(F.text == BTN_VOICE)
async def open_voice_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="🎙 **Ovoz bilan ishlash bo‘limi**\n\nOvozli xabar yuborishingiz yoki amalni tanlashingiz mumkin:",
        reply_markup=get_voice_menu_keyboard(),
    )


@router.message(F.text == BTN_DOCS)
async def open_docs_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(DocumentStates.waiting_for_pdf)
    await message.answer(
        text="📄 **Hujjat bilan ishlash (PDF)**\n\n"
             "Iltimos, tahlil qilish uchun PDF hujjat yuboring (maksimal 20MB gacha).",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == BTN_EDUCATION)
async def open_education_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="📚 **Ta’lim bo‘limi**\n\nQanday ta'limiy yordam kerak?",
        reply_markup=get_education_menu_keyboard(),
    )


@router.message(F.text == BTN_ENTERTAINMENT)
async def open_entertainment_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="🎮 **Ko‘ngilochar bo‘lim**\n\nKayfiyatni ko‘tarish uchun birini tanlang:",
        reply_markup=get_entertainment_menu_keyboard(),
    )


@router.message(F.text == BTN_NOTES)
async def open_notes_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="📝 **Mening qaydlarim**\n\nQayd yaratishingiz, ko‘rishingiz yoki qidirishingiz mumkin:",
        reply_markup=get_notes_menu_keyboard(),
    )


@router.message(F.text == BTN_REMINDERS)
async def open_reminders_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="⏰ **Eslatmalar bo‘limi**\n\nEslatmalaringizni boshqaring:",
        reply_markup=get_reminders_menu_keyboard(),
    )


@router.message(F.text == BTN_SETTINGS)
async def open_settings_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="⚙️ **Sozlamalar**\n\nQuyidagi sozlamalarni o‘zgartirishingiz mumkin:",
        reply_markup=get_settings_menu_keyboard(),
    )
