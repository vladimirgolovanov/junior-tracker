import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import aio_pika
from fastapi import Request

from src.config import settings

logger = logging.getLogger(__name__)


def format_event_text(
    occurred_at: datetime,
    timezone_str: str | None,
    keywords: list[str] | None,
    volume: int | None,
) -> str | None:
    if not keywords:
        return None
    tz = ZoneInfo(timezone_str) if timezone_str else ZoneInfo("UTC")
    local_dt = occurred_at.astimezone(tz)
    parts = [local_dt.strftime("%H:%M"), keywords[0]]
    if volume is not None:
        parts.append(str(volume))
    return " ".join(parts)


class RabbitPublisher:
    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection) -> None:
        self._connection = connection

    async def publish_event_created(self, event_id: int, chat_id_str: str, text: str) -> None:
        payload = {
            "id": event_id,
            "action": "create",
            "chat_id": int(chat_id_str),
            "text": text,
        }
        channel = await self._connection.channel()
        try:
            await channel.declare_queue(settings.rabbitmq_tg_commands_queue, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.rabbitmq_tg_commands_queue,
            )
            logger.info("Published event_created for event_id=%s", event_id)
        finally:
            await channel.close()

    async def publish_event_updated(
        self, event_id: int, chat_id_str: str, text: str, tg_message_id: int
    ) -> None:
        payload = {
            "id": event_id,
            "action": "update",
            "chat_id": int(chat_id_str),
            "text": text,
            "tg_message_id": tg_message_id,
        }
        channel = await self._connection.channel()
        try:
            await channel.declare_queue(settings.rabbitmq_tg_commands_queue, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.rabbitmq_tg_commands_queue,
            )
            logger.info("Published event_updated for event_id=%s", event_id)
        finally:
            await channel.close()


async def get_publisher(request: Request) -> "RabbitPublisher | None":
    connection = request.app.state.rabbit_connection
    if connection is None:
        return None
    return RabbitPublisher(connection)
