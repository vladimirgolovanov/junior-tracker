from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.services.range_events_builder import RangeEventsBuilder, RangeSegment

EVENT_TYPES = {1: "sleep_start", 2: "sleep_end", 3: "food", 4: "poo", 5: "formula"}


@dataclass
class EventPoint:
    id: int
    type: str
    time: datetime
    description: Optional[str]
    volume_ml: Optional[float]


class TimelineService:
    def get_range_events(
        self, rows: list[dict], event_type_ids: tuple
    ) -> list[RangeSegment]:
        return RangeEventsBuilder().build(rows, event_type_ids)

    def get_single_events(self, rows: list[dict]) -> list[EventPoint]:
        return []
