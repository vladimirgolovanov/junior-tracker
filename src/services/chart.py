from fastapi import Depends, HTTPException
from datetime import date

from sqlalchemy.orm import selectinload

from src.models import User, Child
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.services.daily import TimelineService


class Chart:
    def __init__(
        self,
        service: TimelineService = Depends(TimelineService),
        chart_repository: ChartRepository = Depends(ChartRepository),
        child_repository: ChildRepository = Depends(ChildRepository),
    ):
        self.service = service
        self.chart_repository = chart_repository
        self.child_repository = child_repository

    async def get_chart_data(
        self,
        user: User,
        child_id: int,
        date_from: date = None,
        date_to: date = None,
        event_type_ids: list = None,
    ):
        event_type_ids = tuple(event_type_ids)

        child = await self.child_repository.find(
            child_id, options=[selectinload(Child.users)]
        )

        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")

        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")

        rows = await self.chart_repository.get_range_events(
            child, date_from, date_to, event_type_ids
        )

        return self.service.get_range_events(rows, event_type_ids)

    async def get_sleep_events(
        self,
        user: User,
        child_id: int,
        date_from: date,
        date_to: date,
    ):
        child = await self.child_repository.find(
            child_id, options=[selectinload(Child.users)]
        )

        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")

        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")

        return await self.chart_repository.get_sleep_events(child_id, date_from, date_to)

    async def get_child_status(self, user: User, child_id: int):
        child = await self.child_repository.find(
            child_id, options=[selectinload(Child.users)]
        )

        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")

        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")

        sleep_row = await self.chart_repository.get_sleep_status(child_id)
        if sleep_row:
            is_sleeping = sleep_row["event_type_name"] == "sleep_start"
            sleep_status = {
                "sleeping": is_sleeping,
                "at": sleep_row["occurred_at"],
            }
        else:
            sleep_status = None

        other_events = await self.chart_repository.get_last_events_per_type(child_id)

        return {"sleep": sleep_status, "last_events": other_events}
