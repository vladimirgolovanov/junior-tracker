from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Child
from src.repositories.base import BaseRepository


class ChildRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(model=Child, db=db)

    async def get_by_tg_chat_id(self, tg_chat_id: str) -> Child | None:
        return await self.find_first_by_column("tg_chat_id", tg_chat_id)
