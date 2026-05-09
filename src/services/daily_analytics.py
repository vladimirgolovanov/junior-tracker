from fastapi import Depends, HTTPException
from sqlalchemy.orm import selectinload

from src.models import Child, User
from src.models.daily_analytics import DailyAnalytics
from src.repositories.child import ChildRepository
from src.repositories.daily_analytics import DailyAnalyticsRepository


class DailyAnalyticsService:
    def __init__(
        self,
        child_repository: ChildRepository = Depends(ChildRepository),
        analytics_repository: DailyAnalyticsRepository = Depends(DailyAnalyticsRepository),
    ):
        self.child_repository = child_repository
        self.analytics_repository = analytics_repository

    async def get_last_14_days(self, child_id: int, user: User) -> list[DailyAnalytics]:
        child = await self.child_repository.find(child_id, options=[selectinload(Child.users)])
        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")
        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")
        return await self.analytics_repository.get_last_n_days(child_id, 14)
