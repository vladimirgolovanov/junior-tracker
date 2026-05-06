from datetime import datetime

from src.constants.sleep import DAY_START, DAY_END
from src.domain.services.sleep_summary_calculator import SleepSummaryCalculator


class CycleDaySleepData:
    def build(
        self,
        rows: list[dict],
        event_type_ids: tuple,
        is_today: bool = False,
        current_time: datetime = None,
    ) -> dict:
        sleep_start_id, sleep_end_id = event_type_ids

        if len(rows) < 2:
            return self._build_empty(
                rows, sleep_start_id, sleep_end_id, is_today, current_time
            )

        segments = self._build_segments(
            rows, sleep_start_id, sleep_end_id, current_time if is_today else None
        )
        day_sleeps, night_sleeps = self._build_sleep_segments(segments)
        sum_data = SleepSummaryCalculator().calculate(rows, event_type_ids)

        current_sleep, current_awake = 0, 0
        if is_today:
            current_sleep, current_awake = self._apply_open_segment(
                rows, sleep_start_id, sleep_end_id, current_time, sum_data
            )

        night_segments = [s for s in segments if s["segment_type"] == "night_sleep"]
        bedtime = night_segments[0]["start_dt"] if night_segments else None

        result = {
            "segments": segments,
            "bedtime": bedtime,
            "current_sleep": int(current_sleep // 60),
            "current_awake": int(current_awake // 60),
            "total_sleep_duration": int(sum_data["total_sleep"] // 60),
            "night_sleep_duration": sum(s["time"] for s in night_sleeps),
            "day_sleep_duration": sum(s["time"] for s in day_sleeps),
            "total_awake_duration": int(sum_data["total_awake"] // 60),
            "day_awake_duration": int(sum_data["day_awake"] // 60),
            "night_awake_duration": int(sum_data["night_awake"] // 60),
            "night_sleep_end": rows[-1]["occurred_at"] if rows else None,
            "awake_time": rows[0]["occurred_at"] if rows else None,
            "cycle_length": int(sum_data["cycle_length"] // 60),
        }

        if is_today:
            result["is_current_asleep"] = rows[-1]["event_type_id"] == sleep_start_id

        return result

    def _build_empty(
        self,
        rows: list[dict],
        sleep_start_id,
        sleep_end_id,
        is_today: bool,
        current_time: datetime,
    ) -> dict:
        current_sleep, current_awake = 0, 0

        if is_today and rows:
            delta = (current_time - rows[-1]["occurred_at"]).total_seconds()
            if rows[-1]["event_type_id"] == sleep_start_id:
                current_sleep = delta
            elif rows[-1]["event_type_id"] == sleep_end_id:
                current_awake = delta

        result = {
            "segments": [],
            "bedtime": None,
            "current_sleep": int(current_sleep // 60),
            "current_awake": int(current_awake // 60),
            "total_sleep_duration": 0,
            "night_sleep_duration": 0,
            "day_sleep_duration": 0,
            "total_awake_duration": 0,
            "day_awake_duration": 0,
            "night_awake_duration": 0,
            "night_sleep_end": None,
            "awake_time": None,
            "cycle_length": 0,
        }

        if is_today:
            result["is_current_asleep"] = (
                rows[-1]["event_type_id"] == sleep_start_id if rows else False
            )

        return result

    def _build_sleep_segments(self, segments: list[dict]) -> tuple[list, list]:
        day_sleeps = [s for s in segments if s["segment_type"] == "day_sleep"]
        night_sleeps = [s for s in segments if s["segment_type"] == "night_sleep"]
        return day_sleeps, night_sleeps

    def _build_segments(
        self,
        rows: list[dict],
        sleep_start_id,
        sleep_end_id,
        current_time: datetime = None,
    ) -> list[dict]:
        day_end_dt = datetime.combine(rows[0]["occurred_at"].date(), DAY_END)

        if rows[0]["event_type_id"] == sleep_end_id:
            wake_up = rows[0]["occurred_at"]
            asleep = rows[1]["occurred_at"]
        else:
            wake_up = rows[1]["occurred_at"]
            asleep = rows[0]["occurred_at"]

        def segment_type(is_sleep, end_dt):
            prefix = "day" if end_dt < day_end_dt else "night"
            suffix = "sleep" if is_sleep else "awake"
            return f"{prefix}_{suffix}"

        segments = [
            {
                "time": int(
                    (rows[1]["occurred_at"] - rows[0]["occurred_at"]).total_seconds()
                    // 60
                ),
                "start_dt": rows[0]["occurred_at"],
                "end_dt": rows[1]["occurred_at"],
                "segment_type": segment_type(
                    rows[0]["event_type_id"] == sleep_start_id, rows[1]["occurred_at"]
                ),
            }
        ]

        for row in rows[2:]:
            if row["event_type_id"] == sleep_start_id:
                segments.append(
                    {
                        "time": int(
                            (row["occurred_at"] - wake_up).total_seconds() // 60
                        ),
                        "start_dt": wake_up,
                        "end_dt": row["occurred_at"],
                        "segment_type": segment_type(False, row["occurred_at"]),
                    }
                )
                asleep = row["occurred_at"]
            elif row["event_type_id"] == sleep_end_id:
                wake_up = row["occurred_at"]
                segments.append(
                    {
                        "time": int((wake_up - asleep).total_seconds() // 60),
                        "start_dt": asleep,
                        "end_dt": wake_up,
                        "segment_type": segment_type(True, wake_up),
                    }
                )

        if current_time is not None:
            last_row = rows[-1]
            segments.append(
                {
                    "time": int(
                        (current_time - last_row["occurred_at"]).total_seconds() // 60
                    ),
                    "start_dt": last_row["occurred_at"],
                    "end_dt": current_time,
                    "segment_type": segment_type(
                        last_row["event_type_id"] == sleep_start_id, current_time
                    ),
                    "is_current": True,
                }
            )

        return segments

    def _make_sleep_entry(
        self, asleep: datetime, wake_up: datetime, day_end_dt: datetime
    ) -> dict:
        duration = wake_up - asleep
        return {
            "time": int(duration.total_seconds() // 60),
            "segment_type": "day_sleep" if wake_up < day_end_dt else "night_sleep",
        }

    def _apply_open_segment(
        self,
        rows: list[dict],
        sleep_start_id,
        sleep_end_id,
        current_time: datetime,
        sum_data: dict,
    ) -> tuple[float, float]:
        current_sleep, current_awake = 0, 0
        last_row = rows[-1]
        delta = (current_time - last_row["occurred_at"]).total_seconds()

        if last_row["event_type_id"] == sleep_start_id:
            current_sleep = delta
            sum_data["total_sleep"] += current_sleep
            if DAY_START <= last_row["occurred_at"].time() < DAY_END:
                sum_data["day_sleep"] += current_sleep
            else:
                sum_data["night_sleep"] += current_sleep

        elif last_row["event_type_id"] == sleep_end_id:
            current_awake = delta
            sum_data["total_awake"] += current_awake
            if last_row["occurred_at"].time() < DAY_END:
                sum_data["day_awake"] += current_awake
            else:
                sum_data["night_awake"] += current_awake

        return current_sleep, current_awake
