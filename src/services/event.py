from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.models import User
from src.repositories.event import EventRepository
from src.schemas.event import EventCreateInternal


class EventService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repository = EventRepository(db)

    async def create(
        self,
        event: EventCreateInternal,
    ):
        return await self.repository.create(event)

    async def get(self, child_id: int = None, user: User = None):
        # todo: check if child belongs to user
        filters = {"child_id": child_id}
        return await self.repository.get(**filters)
