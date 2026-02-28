from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.repositories.child import ChildRepository


class ChildService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repository = ChildRepository(db)

    async def get_by_chat_id(self, chat_id: str):
        return await self.repository.get_by_tg_chat_id(chat_id)
