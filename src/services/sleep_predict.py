from fastapi import Depends

from src.models import User
from src.repositories.event import EventRepository
from src.repositories.sleep_predict import SleepPredictRepository
from src.services.child_access import ChildAccessGuard


class SleepPredictService:
    def __init__(
        self,
        child_guard: ChildAccessGuard = Depends(ChildAccessGuard),
        event_repository: EventRepository = Depends(EventRepository),
        sleep_predict_repository: SleepPredictRepository = Depends(SleepPredictRepository),
    ):
        self.child_guard = child_guard
        self.event_repository = event_repository
        self.sleep_predict_repository = sleep_predict_repository

    async def get_predictions(self, child_id: int, user: User) -> list:
        await self.child_guard.assert_access(user, child_id)
        event = await self.event_repository.get_last_range_event(child_id)
        if not event:
            return []
        predict = await self.sleep_predict_repository.get_by_child_and_occurred_at(
            child_id, event.occurred_at
        )
        if not predict:
            return []
        return predict.data.get("predictions", [])
