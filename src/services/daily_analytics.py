from fastapi import Depends

from src.models import User
from src.models.daily_analytics import DailyAnalytics
from src.repositories.daily_analytics import DailyAnalyticsRepository
from src.services.child_access import ChildAccessGuard


class DailyAnalyticsService:
    def __init__(
        self,
        child_guard: ChildAccessGuard = Depends(ChildAccessGuard),
        analytics_repository: DailyAnalyticsRepository = Depends(DailyAnalyticsRepository),
    ):
        self.child_guard = child_guard
        self.analytics_repository = analytics_repository

    async def get_last_14_days(self, child_id: int, user: User) -> list[DailyAnalytics]:
        await self.child_guard.assert_access(user, child_id)
        return await self.analytics_repository.get_last_n_days(child_id, 14)
