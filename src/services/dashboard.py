from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from sqlalchemy.orm import selectinload

from src.domain.services.cycle_day_events_isolator import CycleDayEventsIsolator
from src.domain.services.cycle_day_sleep_data import CycleDaySleepData
from src.models import Child, User
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.repositories.event_type import EventTypeRepository


class Dashboard:
    def __init__(
        self,
        child_repository: ChildRepository = Depends(ChildRepository),
        chart_repository: ChartRepository = Depends(ChartRepository),
        event_type_repository: EventTypeRepository = Depends(EventTypeRepository),
    ):
        self.child_repository = child_repository
        self.chart_repository = chart_repository
        self.event_type_repository = event_type_repository

    async def get_last_three_days(
        self,
        child_id: int,
        user: User,
        today: date = None,
        current_time: datetime = None,
    ):
        child = await self.child_repository.find(
            child_id, options=[selectinload(Child.users)]
        )

        child_tz = ZoneInfo(child.timezone)
        current_time = current_time.astimezone(child_tz).replace(tzinfo=None)

        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")

        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")

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
        yesterday_rows = isolator.isolate(yesterday_rows, yesterday_date, event_type_ids)

        today_date = today
        today_rows_a = await self.chart_repository.get_cycle_day_events(
            child, today_date, event_type_ids
        )
        today_rows = isolator.isolate(today_rows_a, today_date, event_type_ids)

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
