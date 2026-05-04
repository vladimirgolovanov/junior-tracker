import logging
from typing import Optional, TYPE_CHECKING

from fastapi import Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.models import User, Event
from src.models.child import Child
from src.models.event_type import EventType
from src.repositories.event import EventRepository
from src.repositories.event_type import EventTypeRepository
from src.schemas.event import EventCreateInternal
from src.services.rabbit_publisher import format_event_text
from src.services.tg_msg_formatter import TgMsgFormatter

if TYPE_CHECKING:
    from src.services.rabbit_publisher import RabbitPublisher

logger = logging.getLogger(__name__)


class EventService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repository = EventRepository(db)
        self.event_type_repository = EventTypeRepository(db)

    async def create(
        self,
        event: EventCreateInternal,
        publisher: "RabbitPublisher | None" = None,
    ):
        db_event = await self.repository.create(event)
        logger.info("event created")

        if publisher:
            logger.info("publishing event")
            try:
                child = (
                    await self.db.execute(
                        select(Child).where(Child.id == db_event.child_id)
                    )
                ).scalar_one_or_none()
                if not child or not child.tg_chat_id:
                    logger.warning(
                        "Skipping publish: child %s has no tg_chat_id",
                        db_event.child_id,
                    )
                    return db_event
                event_types = await self.get_event_types(child.id)
                formatter = TgMsgFormatter(event_types)
                event_type = await self.event_type_repository.find(event.event_type_id)
                if event_type.format == "range_end":
                    start_event = await self.repository.get(
                        limit=1,
                        order_by="occurred_at",
                        order_dir="desc",
                        event_type_id=event_type.parent_id,
                    )

                    message_text = formatter.format(
                        start_event[0].__dict__,
                        db_event.__dict__,
                    )

                    logger.info("message_text: " + message_text)
                    await publisher.publish_event_updated(
                        db_event.id,
                        child.tg_chat_id,
                        message_text,
                        start_event[0].tg_message_id,
                    )
                else:
                    message_text = formatter.format(db_event.__dict__)
                    logger.info("message_text: " + message_text)
                    await publisher.publish_event_created(
                        db_event.id, child.tg_chat_id, message_text
                    )
            except Exception:
                logger.exception(
                    "Failed to publish RabbitMQ message for event_id=%s", db_event.id
                )

        return db_event

    async def set_tg_msg_id(self, record_id: int, tg_msg_id: int) -> Optional[Event]:
        return await self.repository.update(record_id, tg_message_id=tg_msg_id)

    async def update_or_create(
        self,
        event: EventCreateInternal,
        events_count: int = 1,
    ):
        return await self.repository.update_or_create(event, events_count=events_count)

    async def get(self, user: User, child_id: int, **kwargs):
        # todo: check if child belongs to user
        return await self.repository.get(child_id=child_id, **kwargs)

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
