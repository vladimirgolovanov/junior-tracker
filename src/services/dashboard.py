import logging
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import aiohttp
from fastapi import Depends

from src.config import settings
from src.domain.services.cycle_day_events_isolator import CycleDayEventsIsolator
from src.domain.services.cycle_day_sleep_data import CycleDaySleepData
from src.models import User
from src.repositories.chart import ChartRepository
from src.repositories.event import EventRepository
from src.repositories.event_type import EventTypeRepository
from src.services.child_access import ChildAccessGuard

logger = logging.getLogger(__name__)


class Dashboard:
    def __init__(
        self,
        child_guard: ChildAccessGuard = Depends(ChildAccessGuard),
        chart_repository: ChartRepository = Depends(ChartRepository),
        event_type_repository: EventTypeRepository = Depends(EventTypeRepository),
        event_repository: EventRepository = Depends(EventRepository),
    ):
        self.child_guard = child_guard
        self.chart_repository = chart_repository
        self.event_type_repository = event_type_repository
        self.event_repository = event_repository

    async def get_last_three_days(
        self,
        child_id: int,
        user: User,
        today: date = None,
        current_time: datetime = None,
    ):
        if not settings.backend_v2_url:
            return

        if today is None:
            today = date.today()

        from_date = today - timedelta(days=2)
        params = {
            "from": from_date.strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d"),
        }

        try:
            url = (
                f"{settings.backend_v2_url}internal/children/{child_id}/sleep-summaries"
            )
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    return result
        except (aiohttp.ClientError, OSError) as e:
            logger.error("Dashboard request failed: %s", e)
            return

        child = await self.child_guard.assert_access(user, child_id)

        child_tz = ZoneInfo(child.timezone)
        current_time = current_time.astimezone(child_tz).replace(tzinfo=None)

        event_type_ids = await self.event_type_repository.get_sleep_event_types(
            child.id
        )

        if today is None:
            today = datetime.now().date()

        isolator = CycleDayEventsIsolator()
        builder = CycleDaySleepData()

        day_before_yesterday_date = today - timedelta(days=2)
        day_before_yesterday_rows = await self.chart_repository.get_cycle_day_events(
            child, day_before_yesterday_date, event_type_ids
        )
        day_before_yesterday_rows = isolator.isolate(
            day_before_yesterday_rows, day_before_yesterday_date, event_type_ids
        )

        yesterday_date = today - timedelta(days=1)
        yesterday_rows = await self.chart_repository.get_cycle_day_events(
            child, yesterday_date, event_type_ids
        )
        yesterday_rows = isolator.isolate(
            yesterday_rows, yesterday_date, event_type_ids
        )

        today_date = today
        today_rows = await self.chart_repository.get_cycle_day_events(
            child, today_date, event_type_ids
        )
        today_rows = isolator.isolate(today_rows, today_date, event_type_ids)

        return {
            "today": builder.build(
                today_rows,
                event_type_ids,
                True,
                current_time,
            ),
            "yesterday": builder.build(yesterday_rows, event_type_ids),
            "day_before_yesterday": builder.build(
                day_before_yesterday_rows, event_type_ids
            ),
        }
