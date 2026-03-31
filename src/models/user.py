from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.child import Child
    from src.models import APIKey


class User(Base, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    childs: Mapped[list["Child"]] = relationship(
        "Child",
        secondary="child_users",
        back_populates="users",
    )

    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )
