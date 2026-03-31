from src.constants.sleep import DAY_START, DAY_END
from src.domain.utils import fmt


class SleepSummaryCalculator:
    def calculate(self, rows: list, event_types: tuple) -> dict:
        sleep_id, wake_id = event_types

        total_sleep = 0
        night_sleep = 0
        day_sleep = 0
        day_awake = 0
        night_awake = 0

        asleep_at = None
        awake_at = None

        for row in rows:
            if row["event_type_id"] == sleep_id:
                if awake_at is not None:
                    awake_seconds = (row["occurred_at"] - awake_at).total_seconds()
                    if awake_at.time() < DAY_END:
                        day_awake += awake_seconds
                    else:
                        night_awake += awake_seconds
                asleep_at = row["occurred_at"]

            elif row["event_type_id"] == wake_id:
                awake_at = row["occurred_at"]
                if asleep_at is None:
                    continue
                duration = (row["occurred_at"] - asleep_at).total_seconds()
                total_sleep += duration

                if DAY_START <= asleep_at.time() < DAY_END:
                    day_sleep += duration
                else:
                    night_sleep += duration

                asleep_at = None

        return {
            "total_sleep": fmt(total_sleep),
            "night_sleep": fmt(night_sleep),
            "day_sleep": fmt(day_sleep),
            "total_awake": fmt(day_awake + night_awake),
            "day_awake": fmt(day_awake),
            "night_awake": fmt(night_awake),
        }
