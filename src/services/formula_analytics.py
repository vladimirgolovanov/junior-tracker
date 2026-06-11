from datetime import date, timedelta

from fastapi import Depends

from src.models import User
from src.repositories.chart import ChartRepository
from src.services.child_access import ChildAccessGuard


class FormulaAnalyticsService:
    def __init__(
        self,
        child_guard: ChildAccessGuard = Depends(ChildAccessGuard),
        chart_repository: ChartRepository = Depends(ChartRepository),
    ):
        self.child_guard = child_guard
        self.chart_repository = chart_repository

    async def get_formula_daily(
        self,
        child_id: int,
        user: User,
        date_from: date | None,
        date_to: date | None,
    ) -> list[dict]:
        child = await self.child_guard.assert_access(user, child_id)

        effective_date_to = date_to or date.today()
        effective_date_from = date_from or (effective_date_to - timedelta(days=29))

        rows = await self.chart_repository.get_formula_daily(
            child, effective_date_from, effective_date_to
        )
        return [
            {"date": row["day"], "total_volume": row["total_volume"], "count": row["count"]}
            for row in rows
        ]
