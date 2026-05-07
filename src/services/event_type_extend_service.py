from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import get_db
from src.models import Child, User
from src.models.event_type import EventType
from src.repositories.child import ChildRepository
from src.repositories.event_type import EventTypeRepository
from src.schemas.event_type import EventTypeCreate, EventTypeUpdate


class EventTypeExtendService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.event_type_repository = EventTypeRepository(db)
        self.child_repository = ChildRepository(db)

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

    async def create(self, user: User, data: EventTypeCreate) -> EventType:
        child = await self.child_repository.find(
            data.child_id, options=[selectinload(Child.users)]
        )
        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")
        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")
        return await self.event_type_repository.create(data)

    async def update(self, user: User, event_type_id: int, data: EventTypeUpdate) -> EventType:
        event_type = await self.event_type_repository.find(event_type_id)
        if event_type is None:
            raise HTTPException(status_code=404, detail="Event type not found")
        child = await self.child_repository.find(
            event_type.child_id, options=[selectinload(Child.users)]
        )
        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")
        update_fields = data.model_dump(exclude_none=True)
        if not update_fields:
            return event_type
        return await self.event_type_repository.update(event_type_id, **update_fields)
