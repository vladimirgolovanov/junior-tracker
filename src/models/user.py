from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import Mapped, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.child import Child


class User(Base, SQLAlchemyBaseUserTable):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    children: Mapped[list["Child"]] = relationship(
        "Child",
        secondary="child_users",
        back_populates="users",
    )
