# 🤖 O‘zbek AI Yordamchi - Telegram Bot

**O‘zbek AI Yordamchi** — bu 100% o‘zbek tilida ishlaydigan, foydalanuvchilarga turli sohalarda yordam beruvchi ko‘p funksiyali Telegram boti. Bot barcha javoblarni, tugmalarni, xatoliklarni va AI tizim ko‘rsatmalarini toza o‘zbek tilida taqdim etadi. Foydalanuvchi boshqa tilda yozsa ham, bot o‘zbek tilida javob qaytaradi.

---

## 🌟 Imkoniyatlar (Asosiy Bo‘limlar)

1. 🧠 **Sun’iy intellekt:**
   - 💬 *AI bilan suhbat*: Oxirgi xabarlar kontekstini saqlagan holda erkin muloqot.
   - 💡 *G‘oya yaratish*: Har qanday mavzuda kreativ va innovatsion g‘oyalar.
   - 🎯 *Qaror qabul qilish*: Variant A va B, afzalliklar, kamchiliklar, xavflar, imkoniyatlar va xolis tavsiya.
   - 🧠 *Fikrni tahlil qilish*: Kuchli va zaif tomonlar, mantiqiy xatolar tahlili.
   - 🔎 *Muammoni tahlil qilish*: Ildiz sabablar va qadamma-qadam yechimlar.
   - 🧑‍💻 *Dasturlash yordamchisi*: Clean code, debug, refactoring va texnik tushuntirish.

2. ✍️ **Matn bilan ishlash:**
   - 📝 *Matn yozish*, ✨ *Matnni yaxshilash* (grammatika va uslub), 📌 *Matnni qisqartirish*.
   - 🔄 *Qayta yozish*, 🌐 *Tarjima qilish*, 📋 *Reja tuzish*, 💼 *Rasmiy matn*, 📱 *Ijtimoiy tarmoq posti*.

3. 📸 **Rasm bilan ishlash (Vision):**
   - 🔍 *Rasmni tahlil qilish*, 📝 *Rasmdagi matnni aniqlash (OCR)*, ❓ *Rasm haqida savol berish*.

4. 🎙 **Ovoz bilan ishlash:**
   - 📝 *Ovozni matnga aylantirish (Speech-to-Text)*: Telegram voice message -> OpenAI Whisper.
   - 🗣 *Matnni ovozga aylantirish (Text-to-Speech)*: Matn -> OpenAI TTS -> Telegram voice.

5. 📄 **Hujjat bilan ishlash (PDF):**
   - PDF qabul qilish (20MB gacha, xotira himoyasi bilan).
   - 📖 *Qisqartirish*, 🔍 *Ma’lumot topish*, ❓ *Savol berish*, 📊 *Tahlil qilish*.

6. 📚 **Ta’lim:**
   - 👨‍🏫 *Menga tushuntir (Feynman usuli)*, 📝 *4 variantli test tuzish*, ❓ *Savol-javob*.
   - 📚 *Dars rejasini tuzish*, 🧠 *Bilimimni tekshirish*.

7. 🎮 **Ko‘ngilochar:**
   - 😂 *Meni kuldir (Hazillar)*, 🔥 *Meni tanqid qil (Do‘stona roast)*, 🎭 *Xarakter tahlili*.
   - 🎲 *Tasodifiy topshiriq*, 🕵️ *Sirli vazifa*, ⚔️ *Qarorlar jangi*.

8. 📝 **Shaxsiy Qaydlar (Notes):**
   - CRUD amallari: Yangi qayd yaratish, barcha qaydlarni ko‘rish, qidirish va o‘chirish.

9. ⏰ **Eslatmalar (Reminders):**
   - Erkin o‘zbekcha matndan vaqtni aniqlash (*"Bugun soat 20:00 da onamga qo‘ng‘iroq qilishni eslat"*).
   - Asyncio fon scheduler har 20 soniyada tekshirib, xabarni o‘z vaqtida yuboradi (`Asia/Tashkent` default timezone).

10. 📊 **Faoliyatim (Shaxsiy statistika):**
    - Ishlatilgan AI so‘rovlar, kirish/chiqish tokenlari soni, qaydlar va eslatmalar soni.

11. ⚙️ **Sozlamalar:**
    - Vaqt mintaqasini o‘zgartirish, suhbat tarixini tozalash (yangi suhbat boshlash).

12. 👑 **Admin Panel (`/admin`):**
    - Jami va oxirgi 24 soatdagi faol a'zolar, bugungi va umumiy AI so‘rovlar, sarflangan tokenlar, Top-5 imkoniyatlar va tizim holati.

13. 🛡 **Xavfsizlik va Rate Limiting:**
    - Redis orqali har bir foydalanuvchi uchun so‘rovlar chegarasi (masalan, 1 daqiqada 20 ta so‘rov).
    - Hech qanday ichki xatolik (traceback) yoki API kalitlar foydalanuvchiga chiqmaydi.

---

## 🛠 Texnologiyalar

- **Python 3.12+**
- **aiogram 3.x** (Telegram Bot Framework)
- **PostgreSQL** & **SQLAlchemy 2.x** (Async ORM)
- **asyncpg** (PostgreSQL async drayveri)
- **Alembic** (Ma'lumotlar bazasi migratsiyalari)
- **Redis** (FSM saqlash va Rate Limiting)
- **OpenAI API** (gpt-4o, whisper-1, tts-1)
- **pypdf** (PDF matn ajratish)
- **Pydantic Settings** (Muhit o‘zgaruvchilari validatsiyasi)
- **Docker & Docker Compose** (Konteynerizatsiya)
- **pytest & pytest-asyncio** (Avtomatlashtirilgan testlar)

---

## 📁 Loyiha Strukturasi

```
Bot/
├── app/
│   ├── bot/
│   │   ├── filters/                 # Admin huquqini tekshirish filtri
│   │   ├── handlers/                # Domain bo'yicha ajratilgan barcha Telegram handlerlari
│   │   ├── keyboards/               # Reply va Inline tugmalar
│   │   ├── middlewares/             # User, Rate limit va Logging middlewarelari
│   │   └── states/                  # Aiogram FSM holatlari
│   ├── config/                      # Pydantic Settings konfiguratsiyasi
│   ├── database/
│   │   ├── models/                  # SQLAlchemy 2.0 async modellari
│   │   └── session.py               # Async engine va sessionmaker
│   ├── services/
│   │   ├── ai/
│   │   │   ├── client.py            # OpenAI async client
│   │   │   ├── prompts/             # Domain bo'yicha tizimli promptlar
│   │   │   └── service.py           # Barcha AI amallari va hisob-kitob
│   │   ├── documents/               # PDF xizmati (pypdf)
│   │   ├── notes/                   # Qaydlar boshqaruvi
│   │   ├── reminders/               # Eslatmalar va fon scheduler
│   │   └── speech/                  # Whisper STT va OpenAI TTS
│   └── utils/                       # Xavfsiz logger va xabarlarni bo'lish utilitasi
├── migrations/                      # Alembic async migratsiyalari
├── tests/                           # To'liq mocklangan pytest to'plami
├── .env.example                     # Muhit parametrlari namunasi
├── .gitignore                       # Git ignore
├── alembic.ini                      # Alembic sozlamalari
├── Dockerfile                       # Production konteyner
├── docker-compose.yml               # Bot, Postgres va Redis
├── main.py                          # Asosiy kirish nuqtasi
├── requirements.txt                 # Kutubxonalar ro'yxati
└── README.md                        # Qo'llanma
```

---

## 🚀 O‘rnatish va Ishga Tushirish

### 1. Muhitni sozlash (.env)

`.env.example` faylidan `.env` nusxasini oling va qiymatlarni to‘ldiring:

```bash
cp .env.example .env
```

`.env` faylidagi asosiy parametrlar:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=123456789
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_bot_db
REDIS_URL=redis://localhost:6379/0
```

---

### 2. Mahalliy (Local) Ishga Tushirish

#### a) Virtual muhit yaratish:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

#### b) Bog‘liqliklarni o‘rnatish:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### c) PostgreSQL va Redis ishga tushirish (agar Docker orqali bo'lsa):
```bash
docker run -d --name bot_postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ai_bot_db postgres:16-alpine
docker run -d --name bot_redis -p 6379:6379 redis:7-alpine
```

#### d) Migratsiyalarni qo‘llash:
```bash
alembic upgrade head
```

#### e) Botni ishga tushirish:
```bash
python main.py
```

---

### 3. Docker Compose orqali Ishga Tushirish (Tavsiya etiladi)

Bitta buyruq bilan PostgreSQL, Redis va Botni konteynerlarda parallel ishga tushirish:

```bash
docker-compose up --build -d
```

Loglarni kuzatish:
```bash
docker-compose logs -f bot
```

To‘xtatish:
```bash
docker-compose down
```

---

## 🧪 Testlarni Ishga Tushirish

Barcha testlar OpenAI API'ni mock qiladi va in-memory SQLite bazasida ishlaydi (haqiqiy API pul sarflanmaydi va tashqi bazaga ehtiyoj yo‘q):

```bash
pytest -v
```

---

## 📋 Xulosa

Ushbu bot qat'iy standartlarga asoslangan:
- Hech qanday ortiqcha overengineering (CQRS, keraksiz repo pattern) yo‘q.
- Toza qatlamlar: **Handler -> FSM/Validation -> Service -> Database/OpenAI API**.
- 100% o‘zbek tilida to‘liq foydalanuvchi tajribasi (UX).
