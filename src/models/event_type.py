from sqlalchemy import String, ForeignKey, ARRAY, Text, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class EventType(Base):
    __tablename__ = "event_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    format: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("event_types.id"), nullable=True
    )
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    show_in_last_events: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    show_in_quick_actions: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    child_id: Mapped[int] = mapped_column(ForeignKey("childs.id"))
