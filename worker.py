import asyncio
from datetime import datetime
import logging
import signal

import sentry_sdk

from src.config import settings
from src.rabbit_worker import RabbitWorker
from src.services.child import ChildService
from src.services.event import EventService
from src.services.tg_msg_parser import TgMsgParser
from src.db_helper import db_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("worker")


async def parse_msg(
    body: dict,
):
    async with db_session() as db:
        child_service = ChildService(db)
        event_service = EventService(db)
        child = await child_service.get_by_chat_id(str(body["chat_id"]))
        if not child:
            logger.error(f"Child with chat_id {body['chat_id']} not found")
            return
        event_types = await event_service.get_event_types(child.id)
        parser = TgMsgParser(event_types)
        timestamp = datetime.fromisoformat(body["timestamp"])
        events = parser.parse_entry(
            body["text"],
            timestamp,
            child.id,
            child.timezone,
            body.get("message_id"),
        )
        for event in events:
            await event_service.update_or_create(event, len(events))


async def handle_tg_commands_responses(body: dict):
    logger.info("Received tg commands response: %s", body)
    try:
        async with db_session() as db:
            event_service = EventService(db)
            result = await event_service.set_tg_msg_id(body.get("id"), body.get("tg_message_id"))
            if result is None:
                logger.warning("set_tg_msg_id: event id=%s not found", body.get("id"))
            else:
                logger.info("set_tg_msg_id: updated event id=%s tg_message_id=%s", result.id, result.tg_message_id)
    except Exception as e:
        logger.exception("Error handling tg commands response: %s", e)
        sentry_sdk.capture_exception(e)
        raise


async def main():
    worker1 = RabbitWorker(settings.rabbit_url, settings.queue_name, handler=parse_msg)
    worker2 = RabbitWorker(
        settings.rabbit_url,
        settings.rabbitmq_tg_commands_responses_queue,
        handler=handle_tg_commands_responses,
    )

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(asyncio.gather(worker1.stop(), worker2.stop())),
        )

    try:
        await asyncio.gather(worker1.start(), worker2.start())
    except asyncio.CancelledError:
        pass
    finally:
        await asyncio.gather(worker1.stop(), worker2.stop())


if __name__ == "__main__":
    asyncio.run(main())
