from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.child import Child
    from src.models.event_type import EventType


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    tg_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    child_id: Mapped[int] = mapped_column(ForeignKey("childs.id"))
    child: Mapped["Child"] = relationship(back_populates="events")

    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id"))
    event_type: Mapped["EventType"] = relationship()
