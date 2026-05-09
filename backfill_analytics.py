import asyncio
import datetime
import logging
from zoneinfo import ZoneInfo

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.models import Child
from src.services.update_analytics import UpdateAnalytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("backfill_analytics")


async def backfill(db: AsyncSession):
    children = (await db.execute(select(Child))).scalars().all()
    logger.info("Found %d children", len(children))

    for child in children:
        rows = (
            await db.execute(
                text("""
                    SELECT DISTINCT (occurred_at AT TIME ZONE :tz)::date AS day
                    FROM events
                    WHERE child_id = :child_id
                    ORDER BY day
                """),
                {"tz": child.timezone, "child_id": child.id},
            )
        ).all()

        days = [row.day for row in rows]
        logger.info("Child %d (%s): %d days to backfill", child.id, child.name, len(days))

        service = UpdateAnalytics(db)
        child_tz = ZoneInfo(child.timezone)
        for day in days:
            # midnight in child's local timezone — astimezone(child_tz).date() == day
            occurred_at = datetime.datetime(day.year, day.month, day.day, tzinfo=child_tz)
            try:
                await service.update(child.id, occurred_at)
                logger.info("  child %d, day %s — done", child.id, day)
            except Exception:
                logger.exception("  child %d, day %s — failed", child.id, day)


async def main():
    async for db in get_db():
        await backfill(db)


if __name__ == "__main__":
    asyncio.run(main())
