import secrets
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models import User, Child


class ChildInvite(Base):
    __tablename__ = "child_invites"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    child_id: Mapped[int] = mapped_column(ForeignKey("childs.id"), nullable=False)
    accepted_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    child: Mapped["Child"] = relationship("Child")
    inviter: Mapped["User"] = relationship("User", foreign_keys=[inviter_id])
    accepted_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[accepted_by_id]
    )

    @staticmethod
    def generate_code() -> str:
        return secrets.token_urlsafe(16)
