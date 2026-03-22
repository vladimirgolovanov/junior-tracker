from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

EVENT_TYPES = {1: "sleep_start", 2: "sleep_end", 3: "food", 4: "poo", 5: "formula"}


@dataclass
class RangeSegment:
    day: str
    start: datetime
    end: datetime

    @property
    def duration(self) -> int:
        return round((self.end - self.start).total_seconds() / 60)


@dataclass
class EventPoint:
    id: int
    type: str
    time: datetime
    description: Optional[str]
    volume_ml: Optional[float]


class TimelineService:
    def get_range_events(self, rows: list[dict]) -> list[RangeSegment]:
        events = sorted(
            [
                {
                    "type": r["event_type_id"],
                    "dt": r["occurred_at"],
                }
                for r in rows
            ],
            key=lambda x: x["dt"],
        )

        pairs = []
        pending_start = None

        for ev in events:
            day = ev["dt"].date()

            if ev["type"] == 1:
                if pending_start is not None:
                    prev_day = pending_start.date()
                    end_of_day = datetime(
                        prev_day.year, prev_day.month, prev_day.day, 23, 59, 59
                    )
                    self.add_pair(pairs, pending_start, end_of_day)
                pending_start = ev["dt"]

            elif ev["type"] == 2:
                if pending_start is not None:
                    self.add_pair(pairs, pending_start, ev["dt"])
                    pending_start = None
                else:
                    start_of_day = datetime(day.year, day.month, day.day, 0, 0, 0)
                    self.add_pair(pairs, start_of_day, ev["dt"])

        if pending_start is not None:
            prev_day = pending_start.date()
            end_of_day = datetime(
                prev_day.year, prev_day.month, prev_day.day, 23, 59, 59
            )
            self.add_pair(pairs, pending_start, end_of_day)

        return pairs

    @staticmethod
    def add_pair(pairs, start, end):
        if start.date() == end.date():
            pairs.append({"day": str(start.date()), "start": start, "end": end})
        else:
            midnight = datetime(end.year, end.month, end.day, 0, 0, 0)
            pairs.append({"day": str(start.date()), "start": start, "end": midnight})
            pairs.append({"day": str(end.date()), "start": midnight, "end": end})

    def get_single_events(self, rows: list[dict]) -> list[EventPoint]:
        return []
