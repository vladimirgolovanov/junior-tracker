from typing import TYPE_CHECKING
from datetime import date

from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.child import Child


class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    child_id: Mapped[int] = mapped_column(ForeignKey("childs.id"))
    child: Mapped["Child"] = relationship(back_populates="daily_analytics")
