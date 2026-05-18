import datetime
import json
from zoneinfo import ZoneInfo

from sqlalchemy import select

from src.domain.services.cycle_day_events_isolator import CycleDayEventsIsolator
from src.domain.services.cycle_day_sleep_data import CycleDaySleepData
from src.models.child import Child
from src.repositories.chart import ChartRepository
from src.repositories.daily_analytics import DailyAnalyticsRepository
from src.repositories.event_type import EventTypeRepository
from src.db_helper import async_session_maker


class UpdateAnalytics:
    async def update(self, child_id: int, occurred_at: datetime.datetime):
        async with async_session_maker() as db:
            try:
                chart_repository = ChartRepository(db)
                event_type_repository = EventTypeRepository(db)
                daily_analytics_repository = DailyAnalyticsRepository(db)

                child = (
                    await db.execute(select(Child).where(Child.id == child_id))
                ).scalar_one()

                child_tz = ZoneInfo(child.timezone)
                event_type_ids = await event_type_repository.get_sleep_event_types(
                    child.id
                )
                day = occurred_at.astimezone(child_tz).date()

                rows = await chart_repository.get_cycle_day_events(
                    child, day, event_type_ids
                )
                rows = CycleDayEventsIsolator().isolate(rows, day, event_type_ids)

                analytics_data = CycleDaySleepData().build(rows, event_type_ids)
                serialized = json.loads(json.dumps(analytics_data, default=str))

                await daily_analytics_repository.upsert(child.id, day, serialized)

                yesterday = day - datetime.timedelta(days=1)
                rows = await chart_repository.get_cycle_day_events(
                    child, yesterday, event_type_ids
                )
                rows = CycleDayEventsIsolator().isolate(rows, yesterday, event_type_ids)

                analytics_data = CycleDaySleepData().build(rows, event_type_ids)
                serialized = json.loads(json.dumps(analytics_data, default=str))

                await daily_analytics_repository.upsert(child.id, yesterday, serialized)

                await db.commit()
            except Exception:
                await db.rollback()
                raise
