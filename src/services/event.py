from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.repositories.event import EventRepository


class EventService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repository = EventRepository(db)

    async def create(
        self,
        event,
    ):
        return await self.repository.create(event)
