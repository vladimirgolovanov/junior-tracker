from datetime import datetime

from src.constants.sleep import DAY_START, DAY_END
from src.domain.utils import fmt
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
        current_awake = 0
        current_sleep = 0
        if len(rows) < 2:
            if is_today and rows:
                if rows[-1]["event_type_id"] == sleep_start_id:
                    delta = current_time - rows[-1]["occurred_at"]
                    current_sleep = delta.total_seconds()
                if rows[-1]["event_type_id"] == sleep_end_id:
                    delta = current_time - rows[-1]["occurred_at"]
                    current_awake = delta.total_seconds()
            return {
                "day_sleeps": [],
                "night_sleeps": [],
                "current_sleep": fmt(current_sleep),
                "current_awake": fmt(current_awake),
                "total_sleep_duration": "0m",
                "night_sleep_duration": "0m",
                "day_sleep_duration": "0m",
                "total_awake_duration": "0m",
                "day_awake_duration": "0m",
                "night_awake_duration": "0m",
                "night_sleep_end": None,
            }
        day_sleeps = []
        if rows[0]["event_type_id"] == sleep_end_id:
            wake_up = rows[0]["occurred_at"]
            asleep = rows[1]["occurred_at"]
            day_sleeps.append({"wake_up": f"{wake_up.strftime('%H:%M')}"})
            awake_time = asleep - wake_up
            hours, remainder = divmod(awake_time.total_seconds(), 3600)
            minutes = remainder // 60
            day_sleeps.append(
                {
                    "awake_time": (
                        f"{int(hours)}h {int(minutes)}m"
                        if hours
                        else f"{int(minutes)}m"
                    ),
                }
            )
        else:
            wake_up = rows[1]["occurred_at"]
            asleep = rows[0]["occurred_at"]
            day_sleeps.append({"wake_up": f"{wake_up.strftime('%H:%M')}"})

        day_end_dt = datetime.combine(rows[0]["occurred_at"].date(), DAY_END)
        night_sleeps = []
        for row in rows[2:]:
            if row["event_type_id"] == sleep_start_id:
                awake_time = row["occurred_at"] - wake_up
                hours, remainder = divmod(awake_time.total_seconds(), 3600)
                minutes = remainder // 60
                awake_entry = {
                    "awake_time": (
                        f"{int(hours)}h {int(minutes)}m"
                        if hours
                        else f"{int(minutes)}m"
                    ),
                }
                (day_sleeps if wake_up < day_end_dt else night_sleeps).append(
                    awake_entry
                )
                asleep = row["occurred_at"]
            elif row["event_type_id"] == sleep_end_id:
                sleep_time = row["occurred_at"] - asleep
                wake_up = row["occurred_at"]
                hours, remainder = divmod(sleep_time.total_seconds(), 3600)
                minutes = remainder // 60
                sleep_entry = {
                    "sleep_time": (
                        f"{int(hours)}h {int(minutes)}m"
                        if hours
                        else f"{int(minutes)}m"
                    ),
                    "sleep_start": f"{asleep.strftime('%H:%M')}",
                    "wake_up": f"{wake_up.strftime('%H:%M')}",
                }
                (day_sleeps if asleep < day_end_dt else night_sleeps).append(
                    sleep_entry
                )

        sum_data = SleepSummaryCalculator().calculate(rows, event_type_ids)

        if is_today:
            if rows[-1]["event_type_id"] == sleep_start_id:
                delta = current_time - rows[-1]["occurred_at"]
                current_sleep = delta.total_seconds()
                sum_data["total_sleep"] += current_sleep
                if DAY_START <= rows[-1]["occurred_at"].time() < DAY_END:
                    sum_data["day_sleep"] += current_sleep
                else:
                    sum_data["night_sleep"] += current_sleep
            if rows[-1]["event_type_id"] == sleep_end_id:
                delta = current_time - rows[-1]["occurred_at"]
                current_awake = delta.total_seconds()
                sum_data["total_awake"] += current_awake
                if rows[-1]["occurred_at"].time() < DAY_END:
                    sum_data["day_awake"] += current_awake
                else:
                    sum_data["night_awake"] += current_awake

        return {
            "day_sleeps": day_sleeps,
            "night_sleeps": night_sleeps,
            "current_sleep": fmt(current_sleep),
            "current_awake": fmt(current_awake),
            "total_sleep_duration": fmt(sum_data["total_sleep"]),
            "night_sleep_duration": fmt(sum_data["night_sleep"]),
            "day_sleep_duration": fmt(sum_data["day_sleep"]),
            "total_awake_duration": fmt(sum_data["total_awake"]),
            "day_awake_duration": fmt(sum_data["day_awake"]),
            "night_awake_duration": fmt(sum_data["night_awake"]),
            "night_sleep_end": rows[-1]["occurred_at"] if rows else None,
        }
