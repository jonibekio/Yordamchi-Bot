from app.services.ai.prompts.base import BASE_UZBEK_RULE

VISION_ANALYZE_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Yuborilgan rasmni to‘liq, sinchkovlik bilan tahlil qilish va undagi voqelik, obyektlar, ranglar va umumiy kompozitsiyani o‘zbek tilida batafsil ifodalab berish."
)

VISION_OCR_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Rasmda aks etgan har qanday matn, hujjat yozuvlari, belgilar yoki yorliqlarni aniqlash va ularni matn ko‘rinishida o‘qib berish.\n"
    "Matnni aniq, o‘z holicha ko‘chirib yozing va agar kerak bo‘lsa o‘zbek tilida xulosa bering."
)

VISION_QA_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Foydalanuvchi taqdim etgan rasm va unga qo‘shimcha berilgan savolga aniq, mantiqiy va tasvirlarga tayangan holda javob berish."
)
