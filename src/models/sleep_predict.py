from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class SleepPredict(Base):
    __tablename__ = "sleep_predicts"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    child_id: Mapped[int] = mapped_column(ForeignKey("childs.id"))
