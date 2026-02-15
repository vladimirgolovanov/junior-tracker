from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

# Association table: Child <-> User with extra "is_owner" flag
child_users = Table(
    "child_users",
    Base.metadata,
    Column("child_id", ForeignKey("childs.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("is_owner", Boolean, nullable=False, default=False),
)


class Child(Base):
    __tablename__ = "childs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=child_users,
        back_populates="children",
    )
