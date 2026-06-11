from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.auth.users import current_active_user
from src.models import User
from src.services.daily_analytics import DailyAnalyticsService
from src.services.formula_analytics import FormulaAnalyticsService

router = APIRouter()


@router.get("/daily")
async def daily_analytics(
    child_id: Annotated[int, Query()],
    user: User = Depends(current_active_user),
    service: DailyAnalyticsService = Depends(),
):
    records = await service.get_last_14_days(child_id, user)
    return [{"date": r.date, "data": r.data} for r in records]


@router.get("/formula")
async def formula_analytics(
    child_id: Annotated[int, Query()],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    user: User = Depends(current_active_user),
    service: FormulaAnalyticsService = Depends(),
):
    return await service.get_formula_daily(child_id, user, date_from, date_to)
