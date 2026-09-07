from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Asosiy tugmalar nomlari
BTN_AI = "🧠 Sun’iy intellekt"
BTN_TEXT = "✍️ Matn bilan ishlash"
BTN_IMAGE = "📸 Rasm bilan ishlash"
BTN_VOICE = "🎙 Ovoz bilan ishlash"
BTN_DOCS = "📄 Hujjat bilan ishlash"
BTN_EDUCATION = "📚 Ta’lim"
BTN_ENTERTAINMENT = "🎮 Ko‘ngilochar"
BTN_NOTES = "📝 Mening qaydlarim"
BTN_REMINDERS = "⏰ Eslatmalar"
BTN_STATS = "📊 Faoliyatim"
BTN_SETTINGS = "⚙️ Sozlamalar"

BTN_BACK = "⬅️ Orqaga"
BTN_MAIN_MENU = "🏠 Bosh menyu"


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy bosh menyu klaviaturasi"""
    kb = [
        [KeyboardButton(text=BTN_AI), KeyboardButton(text=BTN_TEXT)],
        [KeyboardButton(text=BTN_IMAGE), KeyboardButton(text=BTN_VOICE)],
        [KeyboardButton(text=BTN_DOCS), KeyboardButton(text=BTN_EDUCATION)],
        [KeyboardButton(text=BTN_ENTERTAINMENT), KeyboardButton(text=BTN_NOTES)],
        [KeyboardButton(text=BTN_REMINDERS), KeyboardButton(text=BTN_STATS)],
        [KeyboardButton(text=BTN_SETTINGS)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Orqaga va Bosh menyu tugmasi"""
    kb = [
        [KeyboardButton(text=BTN_BACK), KeyboardButton(text=BTN_MAIN_MENU)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish / Bosh menyu"""
    kb = [
        [KeyboardButton(text=BTN_MAIN_MENU)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
