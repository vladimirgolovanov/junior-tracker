from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.models import Event
from src.repositories.base import BaseRepository, ModelType


class EventRepository(BaseRepository[Event]):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__(model=Event, db=db)

    async def update_or_create(
        self, obj_in: BaseModel, events_count: int, **extra_fields
    ) -> ModelType:
        obj_data = obj_in.model_dump()
        obj_data.update(extra_fields)

        # Поля для поиска
        tg_message_id = obj_data.get("tg_message_id")
        child_id = obj_data.get("child_id")
        event_type_id = obj_data.get("event_type_id")

        # Ищем существующую запись
        stmt = select(self.model).where(
            self.model.tg_message_id == tg_message_id,
            self.model.child_id == child_id,
        )
        result = await self.db.execute(stmt)
        existing_objs = result.scalars().all()

        db_obj = None
        if existing_objs:
            if len(existing_objs) == 1 and events_count == 1:
                db_obj = existing_objs[0]
            else:
                for obj in existing_objs:
                    if obj.event_type_id == event_type_id:
                        db_obj = obj
                        break
                if db_obj is None and events_count == 1:
                    db_obj = existing_objs[0]
        if db_obj:
            # UPDATE
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
        else:
            # CREATE
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)

        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
