from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.models.base import Base


class AIUsage(Base):
    __tablename__ = "ai_usages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    feature: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        index=True,
        nullable=False,
    )

    # Aloqalar
    user: Mapped["User"] = relationship("User", back_populates="ai_usages")

    def __repr__(self) -> str:
        return f"<AIUsage id={self.id} user_id={self.user_id} feature={self.feature} tokens={self.input_tokens}+{self.output_tokens}>"
