from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import get_db
from src.models import Child, User
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.repositories.event_type import EventTypeRepository


class Dashboard:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.child_repository = ChildRepository(db)
        self.chart_repository = ChartRepository(db)
        self.event_type_repository = EventTypeRepository(db)

    async def get_last_three_days(
        self,
        child_id: int,
        user: User,
    ):
        child = await self.child_repository.find(
            child_id, options=[selectinload(Child.users)]
        )

        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")

        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")

        # get sleep events for 3 days (today, yesterday, and the day before yesterday)
        today = datetime.now()
        # yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)

        event_type_ids = await self.event_type_repository.get_sleep_event_types(
            child.id
        )

        rows = await self.chart_repository.get_range_events(
            child, day_before_yesterday, today, event_type_ids
        )

        return rows

        # create data from it
