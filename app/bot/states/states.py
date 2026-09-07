from aiogram.fsm.state import State, StatesGroup


class AIChatStates(StatesGroup):
    chatting = State()
    waiting_for_idea_topic = State()
    waiting_for_decision_topic = State()
    waiting_for_thought = State()
    waiting_for_problem = State()
    waiting_for_coding_question = State()


class TextStates(StatesGroup):
    waiting_for_write_topic = State()
    waiting_for_improve_text = State()
    waiting_for_summarize_text = State()
    waiting_for_rewrite_text = State()
    waiting_for_translate_text = State()
    waiting_for_plan_topic = State()
    waiting_for_formal_topic = State()
    waiting_for_social_topic = State()


class ImageStates(StatesGroup):
    waiting_for_image = State()
    waiting_for_image_qa_question = State()


class VoiceStates(StatesGroup):
    waiting_for_voice = State()
    waiting_for_tts_text = State()


class DocumentStates(StatesGroup):
    waiting_for_pdf = State()
    waiting_for_pdf_qa = State()
    waiting_for_pdf_search = State()


class EducationStates(StatesGroup):
    waiting_for_explain_topic = State()
    waiting_for_quiz_topic = State()
    waiting_for_qa_question = State()
    waiting_for_lesson_topic = State()
    waiting_for_check_topic = State()


class EntertainmentStates(StatesGroup):
    waiting_for_roast_info = State()
    waiting_for_personality_text = State()
    waiting_for_battle_choices = State()


class NoteStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_search_query = State()


class ReminderStates(StatesGroup):
    waiting_for_reminder_text = State()


class SettingsStates(StatesGroup):
    waiting_for_timezone = State()
