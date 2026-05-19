import logging
from datetime import datetime, timedelta

import aiohttp
from sqlalchemy import insert

from src.config import settings
from src.constants.sleep import DAY_END
from src.db_helper import async_session_maker, get_db
from src.models import SleepPredict
from src.repositories.event import EventRepository
from src.repositories.event_type import EventTypeRepository
from src.models.event import Event

logger = logging.getLogger(__name__)


class Predictor:
    PREDICT_LIMIT = 5

    def __init__(self):
        self.event_type_repository = None
        self.event_repository = None

    async def predict(self, child_id: int, event_type_id: int, occurred_at: datetime):
        if not settings.predict_url:
            return

        async with async_session_maker() as db:
            self.event_type_repository = EventTypeRepository(db)
            self.event_repository = EventRepository(db)

            event_type_ids = await self.event_type_repository.get_sleep_event_types(
                child_id
            )
            if event_type_id not in event_type_ids:
                return

            current_day_events = await self.get_current_day(child_id, occurred_at, db)
            payload = {
                "start_dt": occurred_at.strftime("%Y-%m-%d %H:%M:%S"),
                "n_segments": self.PREDICT_LIMIT,
                "current_day": current_day_events,
            }
            logger.info("Sending predict request: %s", payload)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        str(settings.predict_url), json=payload
                    ) as response:
                        result = await response.json()
                        logger.info(
                            "Predict response [%s]: %s", response.status, result
                        )
                        await db.execute(
                            insert(SleepPredict).values(
                                child_id=child_id,
                                occurred_at=occurred_at,
                                data=result,
                            )
                        )
                        await db.commit()
            except (aiohttp.ClientError, OSError) as e:
                logger.error("Predict request failed: %s", e)

    async def get_current_day(self, child_id: int, occurred_at: datetime, db):
        event_type_ids = await self.event_type_repository.get_sleep_event_types(
            child_id
        )

        filters = {
            "child_id": child_id,
            "occurred_at__gte": occurred_at.replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            "occurred_at__lt": occurred_at.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            + timedelta(days=1),
            "event_type_id__in": event_type_ids,
        }
        current_day_events = await self.event_repository.get(**filters)

        segments = _events_to_segments(current_day_events, event_type_ids)

        return segments


def _events_to_segments(events: list[Event], event_type_ids: tuple) -> list[dict]:
    start_type, end_type = event_type_ids

    if len(events) < 2:
        return []

    events = sorted(events, key=lambda e: e.occurred_at)
    day_end_dt = datetime.combine(
        events[0].occurred_at.date(), DAY_END, tzinfo=events[0].occurred_at.tzinfo
    )

    def seg_type(is_sleep: bool, end_dt: datetime) -> str:
        prefix = "day" if end_dt < day_end_dt else "night"
        suffix = "sleep" if is_sleep else "awake"
        return f"{prefix}_{suffix}"

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    if events[0].event_type_id == end_type:
        wake_up = events[0].occurred_at
        asleep = events[1].occurred_at
    else:
        wake_up = events[1].occurred_at
        asleep = events[0].occurred_at

    segments = [
        {
            "time": int(
                (events[1].occurred_at - events[0].occurred_at).total_seconds() / 60
            ),
            "start_dt": fmt(events[0].occurred_at),
            "end_dt": fmt(events[1].occurred_at),
            "segment_type": seg_type(
                events[0].event_type_id == start_type, events[1].occurred_at
            ),
        }
    ]

    for event in events[2:]:
        if event.event_type_id == start_type:
            segments.append(
                {
                    "time": int((event.occurred_at - wake_up).total_seconds() / 60),
                    "start_dt": fmt(wake_up),
                    "end_dt": fmt(event.occurred_at),
                    "segment_type": seg_type(False, event.occurred_at),
                }
            )
            asleep = event.occurred_at
        elif event.event_type_id == end_type:
            wake_up = event.occurred_at
            segments.append(
                {
                    "time": int((wake_up - asleep).total_seconds() / 60),
                    "start_dt": fmt(asleep),
                    "end_dt": fmt(wake_up),
                    "segment_type": seg_type(True, wake_up),
                }
            )

    return segments
