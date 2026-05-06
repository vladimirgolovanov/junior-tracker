from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.repositories.event_type import EventTypeRepository


class EventTypeExtendService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.event_type_repository = EventTypeRepository(db)

    async def get_event_types(self, child_id: int):
        event_types = await self.event_type_repository.get(child_id=child_id)

        for event_type in event_types:
            if event_type.format in ("range", "range_end"):
                event_type.show_in_filters = False
            else:
                event_type.show_in_filters = True

            if event_type.format == "metric":
                event_type.volume_input = True
            else:
                event_type.volume_input = False

            if event_type.format == "described":
                event_type.describe_input = True
            else:
                event_type.describe_input = False

        return event_types
