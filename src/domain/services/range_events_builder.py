from dataclasses import dataclass
from datetime import datetime


@dataclass
class RangeSegment:
    day: str
    start: datetime
    end: datetime

    @property
    def duration(self) -> int:
        return round((self.end - self.start).total_seconds() / 60)


class RangeEventsBuilder:
    def build(
        self, rows: list[dict], event_type_ids: tuple
    ) -> list[RangeSegment]:
        start_type_id, end_type_id = event_type_ids

        events = sorted(
            [{"type": r["event_type_id"], "dt": r["occurred_at"]} for r in rows],
            key=lambda x: x["dt"],
        )

        pairs = []
        pending_start = None

        for ev in events:
            day = ev["dt"].date()

            if ev["type"] == start_type_id:
                if pending_start is not None:
                    prev_day = pending_start.date()
                    end_of_day = datetime(
                        prev_day.year, prev_day.month, prev_day.day, 23, 59, 59
                    )
                    self._add_pair(pairs, pending_start, end_of_day)
                pending_start = ev["dt"]

            elif ev["type"] == end_type_id:
                if pending_start is not None:
                    self._add_pair(pairs, pending_start, ev["dt"])
                    pending_start = None
                else:
                    start_of_day = datetime(day.year, day.month, day.day, 0, 0, 0)
                    self._add_pair(pairs, start_of_day, ev["dt"])

        if pending_start is not None:
            prev_day = pending_start.date()
            end_of_day = datetime(
                prev_day.year, prev_day.month, prev_day.day, 23, 59, 59
            )
            self._add_pair(pairs, pending_start, end_of_day)

        return pairs

    @staticmethod
    def _add_pair(pairs: list, start: datetime, end: datetime) -> None:
        if start.date() == end.date():
            pairs.append({"day": str(start.date()), "start": start, "end": end})
        else:
            midnight = datetime(end.year, end.month, end.day, 0, 0, 0)
            pairs.append({"day": str(start.date()), "start": start, "end": midnight})
            pairs.append({"day": str(end.date()), "start": midnight, "end": end})
