from typing import TypeVar, Generic, Type, Optional, Any

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.model: Type[ModelType] = model

    async def get(
        self,
        limit: int | None = None,
        offset: int | None = None,
        **filters,
    ) -> list[ModelType]:
        query = select(self.model)
        for field, value in filters.items():
            if value is not None and hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def find(self, id: int) -> ModelType | None:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def find_first_by_column(self, column: str, value: Any) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(getattr(self.model, column) == value)
        )
        return result.scalar_one_or_none()

    async def create(self, obj_in: BaseModel, **extra_fields) -> ModelType:
        obj_data = obj_in.model_dump()
        obj_data.update(extra_fields)
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_or_create(self, obj_in: BaseModel, **extra_fields) -> ModelType:
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
            # Если запись одна, и event_type_id не 1 или 2
            if len(existing_objs) == 1 and event_type_id not in (1, 2):
                db_obj = existing_objs[0]
            else:
                # Несколько записей — берём ту, что совпадает по event_type_id
                for obj in existing_objs:
                    if obj.event_type_id == event_type_id:
                        db_obj = obj
                        break
                # Если ни одна не совпала по event_type_id — берём первую
                # и obj.event_type_id не 1 или 2
                if db_obj is None and event_type_id not in (1, 2):
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

    async def update(self, db_obj: ModelType, obj_in: BaseModel) -> Optional[ModelType]:
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**obj_in)
        )
        await self.db.flush()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        result = await self.db.execute(delete(self.model).where(self.model.id == id))
        await self.db.flush()
        return result.rowcount > 0
