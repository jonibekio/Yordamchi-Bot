from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Tashkent", nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    # Aloqalar
    user: Mapped["User"] = relationship("User", back_populates="reminders")

    __table_args__ = (
        Index("ix_reminders_user_id_remind_at", "user_id", "remind_at"),
    )

    def __repr__(self) -> str:
        return f"<Reminder id={self.id} user_id={self.user_id} remind_at={self.remind_at} completed={self.is_completed}>"
