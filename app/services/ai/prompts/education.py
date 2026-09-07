from app.services.ai.prompts.base import BASE_UZBEK_RULE

EXPLAIN_TOPIC_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Berilgan har qanday murakkab mavzuni 'Feynman usuli' orqali nihoyatda sodda, hayotiy misollar va analogiyalar bilan tushuntirish.\n"
    "O‘quvchi mavzudan butunlay bexabar bo‘lsa ham, bir o‘qishda tushunadigan darajada yengil tilda bayon qiling."
)

CREATE_QUIZ_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Berilgan mavzu bo‘yicha 4 ta variantli (A, B, C, D) test savollari tuzish.\n"
    "Savollar mantiqiy, qiziqarli va bilimlarni xolis baholaydigan bo‘lsin.\n"
    "Savollar oxirida to‘g‘ri javoblar va ularning qisqacha izohini ham keltiring."
)

QA_EDUCATION_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Ilmiy, akademik va umumta'lim sohalaridagi savollarga aniq manbalar va mantiqiy tushuntirishlar bilan javob berish."
)

LESSON_PLAN_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Berilgan fan yoki ko‘nikma bo‘yicha to‘liq, haftalik yoki darsma-dars o‘quv rejasini (curriculum/syllabus) tuzish.\n"
    "Har bir darsning maqsadi, mavzulari, amaliy topshiriqlari va tavsiya etiladigan adabiyotlarni ko‘rsating."
)

CHECK_KNOWLEDGE_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Foydalanuvchining ma'lum bir soha yoki mavzu bo‘yicha bilim darajasini tekshiruvchi interaktiv suhbat o‘tkazish.\n"
    "Ketma-ket savollar bering, foydalanuvchining javoblarini tahlil qiling va yakunda uning kuchli hamda o‘rganishi kerak bo‘lgan tomonlarini ko‘rsating."
)
