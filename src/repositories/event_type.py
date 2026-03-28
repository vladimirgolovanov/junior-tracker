from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.enums.event_types import EventTypeName
from src.models import EventType
from src.repositories.base import BaseRepository


class EventTypeRepository(BaseRepository):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__(model=EventType, db=db)

    async def get_sleep_event_types(self, child_id) -> tuple:
        query = select(EventType).where(
            EventType.child_id == child_id,
            EventType.name.in_([EventTypeName.sleep_start, EventTypeName.sleep_end]),
        )

        rows = (await self.db.execute(query)).scalars().all()
        sleep_types_by_name = {row.name: row.id for row in rows}

        return (
            sleep_types_by_name[EventTypeName.sleep_start],
            sleep_types_by_name[EventTypeName.sleep_end],
        )
