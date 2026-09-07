from datetime import datetime, timedelta
import pytz
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import AdminFilter
from app.database.models.ai_usage import AIUsage
from app.database.models.user import User

router = Router(name="admin")
router.message.filter(AdminFilter())


@router.message(Command("admin"))
async def cmd_admin_panel(
    message: Message,
    db_session: AsyncSession,
) -> None:
    # 1. Jami foydalanuvchilar
    total_users_res = await db_session.execute(select(func.count(User.id)))
    total_users = total_users_res.scalar_one() or 0

    # 2. Aktiv foydalanuvchilar (oxirgi 24 soat ichida faoliyat yuritgan)
    since_24h = datetime.now(pytz.UTC) - timedelta(hours=24)
    active_users_res = await db_session.execute(
        select(func.count(func.distinct(AIUsage.user_id))).where(AIUsage.created_at >= since_24h)
    )
    active_users = active_users_res.scalar_one() or 0

    # 3. Bugungi AI so'rovlar soni
    today_start = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    today_usage_res = await db_session.execute(
        select(func.count(AIUsage.id)).where(AIUsage.created_at >= today_start)
    )
    today_requests = today_usage_res.scalar_one() or 0

    # 4. Umumiy AI so'rovlar va jami tokenlar
    total_ai_res = await db_session.execute(
        select(
            func.count(AIUsage.id),
            func.sum(AIUsage.input_tokens),
            func.sum(AIUsage.output_tokens),
        )
    )
    total_ai_count, total_in_tokens, total_out_tokens = total_ai_res.one()
    total_ai_count = total_ai_count or 0
    total_tokens = (total_in_tokens or 0) + (total_out_tokens or 0)

    # 5. Feature bo'yicha statistika (Top 5)
    features_res = await db_session.execute(
        select(AIUsage.feature, func.count(AIUsage.id).label("cnt"))
        .group_by(AIUsage.feature)
        .order_by(func.count(AIUsage.id).desc())
        .limit(5)
    )
    top_features = features_res.all()

    feature_lines = []
    for feat_name, count in top_features:
        feature_lines.append(f"  • `{feat_name}`: {count} marta")
    feature_text = "\n".join(feature_lines) if feature_lines else "  Hozircha ma'lumot yo‘q"

    admin_text = (
        "👑 **Administrator Paneli - O‘zbek AI Yordamchi**\n\n"
        "📊 **Foydalanuvchilar:**\n"
        f"• Jami a'zolar: **{total_users} nafar**\n"
        f"• Oxirgi 24 soatda faol: **{active_users} nafar**\n\n"
        "🤖 **Sun’iy intellekt statistikasi:**\n"
        f"• Bugungi AI so‘rovlar: **{today_requests} ta**\n"
        f"• Umumiy AI so‘rovlar: **{total_ai_count} ta**\n"
        f"• Jami sarflangan tokenlar: **{total_tokens:,}**\n\n"
        "📈 **Eng ko‘p ishlatilgan imkoniyatlar (Top 5):**\n"
        f"{feature_text}\n\n"
        "🟢 **Tizim holati:**\n"
        "• Ma'lumotlar bazasi: *Faol (PostgreSQL)*\n"
        "• Kesh & Rate Limit: *Faol (Redis)*\n"
        "• Bot statusi: *Ishlamoqda (Online)*"
    )

    await message.answer(admin_text, parse_mode="Markdown")
