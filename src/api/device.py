from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo
from fastapi.responses import PlainTextResponse

from fastapi import APIRouter, Depends

from src.models.api_key import APIKey
from src.services.api_keys import get_api_key
from src.services.event import EventService

router = APIRouter()

UTC = dt_timezone.utc


@router.get("/last_events")
async def events(
    api_key: APIKey = Depends(get_api_key),
    service: EventService = Depends(),
):
    child_id = api_key.child_id
    tz = ZoneInfo(api_key.child.timezone) if api_key.child and api_key.child.timezone else UTC
    now = datetime.now(UTC)

    last_formula = await service.last_formula(child_id)
    if not last_formula:
        return ""

    delta = now - last_formula["occurred_at"].astimezone(UTC)
    total_minutes = int(delta.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    last_f = f"Formula {hours}:{minutes:02d} {last_formula['volume']}"

    last_sleep = await service.last_sleep(child_id)
    sleep = next((r for r in last_sleep if r["event_type_id"] == 1), None)
    sleep_delta = now - sleep["occurred_at"].astimezone(UTC)
    awake = next((r for r in last_sleep if r["event_type_id"] == 2), None)
    awake_delta = now - awake["occurred_at"].astimezone(UTC)
    if sleep_delta > awake_delta:
        total_minutes = int(awake_delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        awsl = f"Awake {hours}:{minutes:02d}"
    else:
        total_minutes = int(sleep_delta.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        awsl = f"Sleep {hours}:{minutes:02d}"

    return PlainTextResponse(f"{awsl}\n{last_f}")
