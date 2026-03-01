from fastapi import Depends
from sqlalchemy import text
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

    async def update_or_create(
        self,
        event: EventCreateInternal,
    ):
        return await self.repository.update_or_create(event)

    async def get(self, child_id: int = None):
        # todo: check if child belongs to user
        filters = {"child_id": child_id}
        return await self.repository.get(**filters)

    async def get_event_types(self, child_id: int):
        query = text("""SELECT id,
                               parent_id
                        FROM event_types
                        WHERE parent_id IS NOT NULL
                        AND child_id = :child_id""")
        rows = (await self.db.execute(query, {"child_id": child_id})).mappings().all()
        yeilds = {row["parent_id"]: row["id"] for row in rows}

        query = text("""SELECT
                   id,
                   format,
                   keywords
            FROM event_types
            WHERE parent_id IS NULL
            AND child_id = :child_id""")
        rows = (await self.db.execute(query, {"child_id": child_id})).mappings().all()

        result = []
        for row in rows:
            event_type_dict = {
                "type": row["format"],
                "keywords": row["keywords"],
            }
            if row["format"] == "range":
                event_type_dict["event_type_id"] = (
                    row["id"],
                    yeilds[row["id"]],
                )
            else:
                event_type_dict["event_type_id"] = row["id"]
            result.append(event_type_dict)
        return result

    async def last_sleep_start(self, child_id: int):
        query = text("""SELECT occurred_at
                        FROM events
                        WHERE child_id = :child_id
                        AND event_type_id = 1
                        ORDER BY occurred_at DESC
                        LIMIT 1""")
        return (await self.db.execute(query, {"child_id": child_id})).mappings().first()

    async def last_formula(self, child_id: int):
        query = text("""SELECT volume, occurred_at
                        FROM events
                        WHERE child_id = :child_id
                        AND event_type_id = 5
                        ORDER BY occurred_at DESC
                        LIMIT 1
        """)
        return (await self.db.execute(query, {"child_id": child_id})).mappings().first()

    async def last_sleep(self, child_id: int):
        query = text("""SELECT event_type_id, occurred_at
                        FROM events
                        WHERE child_id = :child_id
                        AND event_type_id IN (1, 2)
                        ORDER BY occurred_at DESC
                        LIMIT 2
        """)
        return (await self.db.execute(query, {"child_id": child_id})).mappings().all()
