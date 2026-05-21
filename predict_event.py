import argparse
import asyncio
import logging
import sys

from src.db_helper import db_session
from src.repositories.event import EventRepository
from src.services.predictor import Predictor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("predict_event")


async def run(event_id: int):
    async with db_session() as db:
        event_repo = EventRepository(db)
        event = await event_repo.find(event_id)
        if event is None:
            logger.error("Event %d not found", event_id)
            sys.exit(1)

        logger.info(
            "Running predict for event %d (child=%d, event_type=%d, occurred_at=%s)",
            event.id,
            event.child_id,
            event.event_type_id,
            event.occurred_at,
        )

    await Predictor().predict(event.child_id, event.event_type_id, event.occurred_at)
    logger.info("Done")


def main():
    parser = argparse.ArgumentParser(
        description="Run Predictor.predict for a given event ID"
    )
    parser.add_argument("event_id", type=int, help="ID of the event to predict from")
    args = parser.parse_args()
    asyncio.run(run(args.event_id))


if __name__ == "__main__":
    main()
