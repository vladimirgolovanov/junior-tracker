from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException

from src.auth.users import current_active_user
from src.models import User
from src.services.chart import Chart
from src.services.dashboard import Dashboard

router = APIRouter()


@router.get("/")
async def chart(  # todo: validation dates + event_type_ids
    child_id: Annotated[int, Query()],
    date_from: Annotated[date, Query()],
    date_to: Annotated[date, Query()],
    event_type_ids: Annotated[list[int], Query(min_length=1)],
    service: Chart = Depends(),
    user: User = Depends(current_active_user),
):
    if date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must be before date_to")

    return await service.get_chart_data(
        user,
        child_id,
        date_from,
        date_to,
        event_type_ids,
    )


@router.get("/dashboard")
async def dashboard(
    child_id: Annotated[int, Query()],
    today: Annotated[date | None, Query()] = None,
    user: User = Depends(current_active_user),
    service: Dashboard = Depends(),
):
    current_time = datetime.now(tz=timezone.utc)  # todo: if today?
    return await service.get_last_three_days(child_id, user, today, current_time)
