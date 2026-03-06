import asyncio
from datetime import datetime
import json
import logging
import signal

import aio_pika

from src.config import settings
from src.services.child import ChildService
from src.services.event import EventService
from src.services.tg_msg_parser import TgMsgParser
from src.db_helper import db_session, get_db

PREFETCH_COUNT = 10


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("worker")


class RabbitWorker:
    def __init__(
        self,
        rabbit_url: str,
        queue_name: str,
    ):
        self.rabbit_url = rabbit_url
        self.queue_name = queue_name
        self._connection = None
        self._channel = None
        self._queue = None
        self._closing = asyncio.Event()

    async def connect(self):
        logger.info("Connecting to RabbitMQ...")
        self._connection = await aio_pika.connect_robust(self.rabbit_url)
        self._channel = await self._connection.channel()

        await self._channel.set_qos(prefetch_count=PREFETCH_COUNT)

        self._queue = await self._channel.declare_queue(
            self.queue_name,
            durable=True,
        )

        logger.info("Connected and queue declared.")

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process(requeue=False):
            body = json.loads(message.body.decode())
            logger.info("Received message: %s", body)
            await parse_msg(body)
            # await some_service.handle(body)

    async def start(self):
        await self.connect()

        logger.info("Starting consumer...")
        await self._queue.consume(self.process_message)

        await self._closing.wait()

    async def stop(self):
        logger.info("Shutting down worker...")
        self._closing.set()

        if self._connection:
            await self._connection.close()

        logger.info("Worker stopped.")


async def parse_msg(
    body: dict,
):
    async for db in get_db():  # async with get_db() as db:
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
            body.get("message_id"),
        )
        for event in events:
            await event_service.update_or_create(event, len(events))


async def main():
    worker = RabbitWorker(settings.rabbit_url, settings.queue_name)

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(worker.stop()),
        )

    try:
        await worker.start()
    except asyncio.CancelledError:
        pass
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
