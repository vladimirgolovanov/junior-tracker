from fastapi import Depends, HTTPException
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import get_db
from src.models import User, Child
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.services.daily import TimelineService


class Chart:
    def __init__(
        self,
        service: TimelineService = Depends(TimelineService),
        db: AsyncSession = Depends(get_db),
    ):
        self.service = service
        self.chart_repository = ChartRepository(db)
        self.child_repository = ChildRepository(db)

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

        return self.service.get_range_events(rows)
