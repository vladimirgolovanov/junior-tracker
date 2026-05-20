import asyncio
from datetime import datetime
import logging
import signal

from src.config import settings
from src.rabbit_worker import RabbitWorker
from src.services.predictor import Predictor
from src.services.update_analytics import UpdateAnalytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("predict_worker")


async def handle_analytics_task(body: dict):
    task = body.get("task")
    child_id = body["child_id"]
    occurred_at = datetime.fromisoformat(body["occurred_at"])
    if task == "update_analytics":
        await UpdateAnalytics().update(child_id, occurred_at)
    elif task == "predict":
        await Predictor().predict(child_id, body["event_type_id"], occurred_at)
    else:
        logger.warning("Unknown analytics task: %s", task)


async def main():
    worker = RabbitWorker(
        settings.rabbit_url,
        settings.rabbitmq_analytics_queue,
        handler=handle_analytics_task,
    )

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(worker.stop()))

    try:
        await worker.start()
    except asyncio.CancelledError:
        pass
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
