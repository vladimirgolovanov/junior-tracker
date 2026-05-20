import asyncio
import json
import logging

import aio_pika

PREFETCH_COUNT = 10

logger = logging.getLogger(__name__)


class RabbitWorker:
    def __init__(
        self,
        rabbit_url: str,
        queue_name: str,
        handler,
    ):
        self.rabbit_url = rabbit_url
        self.queue_name = queue_name
        self._handler = handler
        self._connection = None
        self._channel = None
        self._queue = None
        self._closing = asyncio.Event()

    async def connect(self):
        logger.info("Connecting to RabbitMQ...")
        self._connection = await aio_pika.connect_robust(self.rabbit_url, heartbeat=60)
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
            await self._handler(body)

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
