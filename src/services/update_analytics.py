import datetime
import json
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.services.cycle_day_events_isolator import CycleDayEventsIsolator
from src.domain.services.cycle_day_sleep_data import CycleDaySleepData
from src.models.child import Child
from src.repositories.chart import ChartRepository
from src.repositories.daily_analytics import DailyAnalyticsRepository
from src.repositories.event_type import EventTypeRepository


class UpdateAnalytics:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chart_repository = ChartRepository(db)
        self.event_type_repository = EventTypeRepository(db)
        self.daily_analytics_repository = DailyAnalyticsRepository(db)

    async def update(self, child_id: int, occurred_at: datetime.datetime):
        child = (
            await self.db.execute(select(Child).where(Child.id == child_id))
        ).scalar_one()

        child_tz = ZoneInfo(child.timezone)
        event_type_ids = await self.event_type_repository.get_sleep_event_types(child.id)
        day = occurred_at.astimezone(child_tz).date()

        rows = await self.chart_repository.get_cycle_day_events(child, day, event_type_ids)
        rows = CycleDayEventsIsolator().isolate(rows, day, event_type_ids)

        analytics_data = CycleDaySleepData().build(rows, event_type_ids)
        serialized = json.loads(json.dumps(analytics_data, default=str))

        await self.daily_analytics_repository.upsert(child.id, day, serialized)
