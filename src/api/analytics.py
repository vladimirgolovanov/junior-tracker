from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.auth.users import current_active_user
from src.models import User
from src.services.daily_analytics import DailyAnalyticsService

router = APIRouter()


@router.get("/daily")
async def daily_analytics(
    child_id: Annotated[int, Query()],
    user: User = Depends(current_active_user),
    service: DailyAnalyticsService = Depends(),
):
    records = await service.get_last_14_days(child_id, user)
    return [{"date": r.date, "data": r.data} for r in records]
