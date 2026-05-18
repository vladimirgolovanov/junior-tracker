from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.models.sleep_predict import SleepPredict
from src.repositories.base import BaseRepository


class SleepPredictRepository(BaseRepository[SleepPredict]):
    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__(model=SleepPredict, db=db)

    async def get_by_child_and_occurred_at(
        self, child_id: int, occurred_at: datetime
    ) -> SleepPredict | None:
        result = await self.db.execute(
            select(SleepPredict).where(
                SleepPredict.child_id == child_id,
                SleepPredict.occurred_at == occurred_at,
            )
        )
        return result.scalar_one_or_none()
