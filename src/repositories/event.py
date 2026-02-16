from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event
from src.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, db: AsyncSession):
        super().__init__(model=Event, db=db)
