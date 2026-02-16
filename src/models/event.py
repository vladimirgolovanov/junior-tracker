from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.models.base import Base

if TYPE_CHECKING:
    from src.models import User
    from src.models.child import Child
    from src.models.event_type import EventType


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="events")

    child_id: Mapped[int] = mapped_column(ForeignKey("childs.id"))
    child: Mapped["Child"] = relationship(back_populates="events")

    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id"))
    event_type: Mapped["EventType"] = relationship()
