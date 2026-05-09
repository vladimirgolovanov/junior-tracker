from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.daily_analytics import DailyAnalytics
from src.repositories.base import BaseRepository


class DailyAnalyticsRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(model=DailyAnalytics, db=db)

    async def upsert(self, child_id: int, day: date, data: dict) -> DailyAnalytics:
        result = await self.db.execute(
            select(DailyAnalytics).where(
                DailyAnalytics.child_id == child_id,
                DailyAnalytics.date == day,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            record.data = data
            await self.db.flush()
            return record
        record = DailyAnalytics(child_id=child_id, date=day, data=data)
        self.db.add(record)
        await self.db.flush()
        return record
