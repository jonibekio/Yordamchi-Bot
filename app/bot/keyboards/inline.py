from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 🧠 Sun'iy intellekt menyusi
def get_ai_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="💬 AI bilan suhbat", callback_data="ai_chat")],
        [InlineKeyboardButton(text="💡 G‘oya yaratish", callback_data="ai_idea")],
        [InlineKeyboardButton(text="🎯 Qaror qabul qilish", callback_data="ai_decision")],
        [InlineKeyboardButton(text="🧠 Fikrni tahlil qilish", callback_data="ai_thought")],
        [InlineKeyboardButton(text="🔎 Muammoni tahlil qilish", callback_data="ai_problem")],
        [InlineKeyboardButton(text="🧑‍💻 Dasturlash yordamchisi", callback_data="ai_coding")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ✍️ Matn vositalari menyusi
def get_text_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="📝 Matn yozish", callback_data="text_write"),
            InlineKeyboardButton(text="✨ Yaxshilash", callback_data="text_improve"),
        ],
        [
            InlineKeyboardButton(text="📌 Qisqartirish", callback_data="text_summarize"),
            InlineKeyboardButton(text="🔄 Qayta yozish", callback_data="text_rewrite"),
        ],
        [
            InlineKeyboardButton(text="🌐 Tarjima qilish", callback_data="text_translate"),
            InlineKeyboardButton(text="📋 Reja tuzish", callback_data="text_plan"),
        ],
        [
            InlineKeyboardButton(text="💼 Rasmiy matn", callback_data="text_formal"),
            InlineKeyboardButton(text="📱 Tarmoq uchun post", callback_data="text_social"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# 📸 Rasm vositalari menyusi
def get_image_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🔍 Rasmni tahlil qilish", callback_data="img_analyze")],
        [InlineKeyboardButton(text="📝 Rasmdagi matnni aniqlash", callback_data="img_ocr")],
        [InlineKeyboardButton(text="❓ Rasm haqida savol berish", callback_data="img_qa")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# 🎙 Ovoz vositalari menyusi
def get_voice_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📝 Ovozdan matnga (STT)", callback_data="voice_stt")],
        [InlineKeyboardButton(text="🗣 Matndan ovozga (TTS)", callback_data="voice_tts")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# 📄 PDF vositalari menyusi
def get_pdf_actions_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📖 Hujjatni qisqartirish", callback_data="pdf_summarize")],
        [InlineKeyboardButton(text="🔍 Ma’lumot topish", callback_data="pdf_search")],
        [InlineKeyboardButton(text="❓ Savol berish", callback_data="pdf_qa")],
        [InlineKeyboardButton(text="📊 Hujjatni tahlil qilish", callback_data="pdf_analyze")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# 📚 Ta'lim menyusi
def get_education_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="👨‍🏫 Menga tushuntir", callback_data="edu_explain")],
        [InlineKeyboardButton(text="📝 Test tuz", callback_data="edu_quiz")],
        [InlineKeyboardButton(text="❓ Savol-javob", callback_data="edu_qa")],
        [InlineKeyboardButton(text="📚 Dars rejasini tuz", callback_data="edu_lesson")],
        [InlineKeyboardButton(text="🧠 Bilimimni tekshir", callback_data="edu_check")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# 🎮 Ko'ngilochar menyusi
def get_entertainment_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="😂 Meni kuldir", callback_data="ent_laugh")],
        [InlineKeyboardButton(text="🔥 Meni tanqid qil", callback_data="ent_roast")],
        [InlineKeyboardButton(text="🎭 Xarakterimni tahlil qil", callback_data="ent_personality")],
        [InlineKeyboardButton(text="🎲 Tasodifiy topshiriq", callback_data="ent_challenge")],
        [InlineKeyboardButton(text="🕵️ Sirli vazifa", callback_data="ent_mystery")],
        [InlineKeyboardButton(text="⚔️ Qarorlar jangi", callback_data="ent_battle")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# 📝 Qaydlar menyusi
def get_notes_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="➕ Yangi qayd", callback_data="note_new")],
        [InlineKeyboardButton(text="📋 Qaydlarim", callback_data="note_list")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="note_search")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_note_item_keyboard(note_id: int) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"note_del_{note_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ⏰ Eslatmalar menyusi
def get_reminders_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="➕ Yangi eslatma", callback_data="reminder_new")],
        [InlineKeyboardButton(text="📋 Eslatmalarim", callback_data="reminder_list")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_reminder_item_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"rem_del_{reminder_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# ⚙️ Sozlamalar menyusi
def get_settings_menu_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="🌍 Vaqt mintaqasi", callback_data="settings_tz")],
        [InlineKeyboardButton(text="🔄 Yangi suhbat boshlash (tarixni tozalash)", callback_data="settings_clear_chat")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
