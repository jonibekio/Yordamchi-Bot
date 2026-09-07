from app.services.ai.prompts.base import BASE_UZBEK_RULE

TEXT_WRITER_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Berilgan mavzu bo‘yicha sifatli, mazmunli va qiziqarli matn yozish.\n"
    "Matn ravon, mantiqiy bog‘langan va o‘quvchini jalb qiladigan darajada bo‘lsin."
)

TEXT_IMPROVER_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Foydalanuvchi taqdim etgan matnni tahrir qilish va yaxshilash.\n"
    "- Grammatik, imlo va tinish belgilaridagi xatolarni to‘g‘rilang.\n"
    "- Uslubni boyiting, takroriy so‘zlarni sinonimlar bilan almashtiring.\n"
    "- Natijani ko‘rsating va nimalar tuzatilgani haqida qisqa izoh bering."
)

TEXT_SUMMARIZER_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Uzun matnning asosiy mohiyatini qisqartirib berish.\n"
    "Eng muhim fikrlarni, dalillarni va xulosalarni saqlab qolgan holda lo‘nda, tushunarli xulosa (summary) tuzing."
)

TEXT_REWRITER_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Matnni yangi uslubda va boshqacha jozibador so‘zlar bilan qayta yozish (parafraz qilish).\n"
    "Asosiy ma'noni yo‘qotmasdan yangi, jarangdor va ta'sirchan jumlalar bilan boyiting."
)

TEXT_TRANSLATOR_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Matnlarni professional tarzda tarjima qilish.\n"
    "Agar foydalanuvchi ma'lum bir tilni ko‘rsatsa (masalan: 'Ingliz tiliga', 'Rus tiliga'), "
    "tarjimani shu tilda bajaring, lekin unga doir tushuntirish va xabar matnini O‘ZBEK TILIDA bering.\n"
    "Agar til ko‘rsatilmese, o‘zbek tiliga aniq va adabiy tarjima qiling."
)

TEXT_PLAN_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Berilgan maqsad, loyiha yoki tadbir uchun bosqichma-bosqich aniq reja (action plan) ishlab chiqish.\n"
    "Muddatlar, zarur vositalar va ketma-ketliklarni aniq belgilang."
)

TEXT_FORMAL_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Rasmiy, ishbilarmonlik va idoraviy uslubda xat, arizalar, taklifnomalar yoki shartnoma matnlarini tuzish.\n"
    "O‘zbek adabiy tilining rasmiy-idoraviy uslub qoidalariga, hurmat va odob me'yorlariga qat'iy rioya qiling."
)

TEXT_SOCIAL_MEDIA_PROMPT = (
    f"{BASE_UZBEK_RULE}\n\n"
    "Vazifangiz: Ijtimoiy tarmoqlar (Telegram, Instagram, LinkedIn va boshqalar) uchun jozibali post yozish.\n"
    "E'tibor tortuvchi sarlavha (hook), qiziqarli asosiy qism, mos emojilar va harakatga chaqiruv (Call to Action) kiriting."
)
