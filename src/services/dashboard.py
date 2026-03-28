from datetime import datetime, timedelta, date

from fastapi import Depends, HTTPException
from sqlalchemy.orm import selectinload

from src.constants.sleep import DAY_START, DAY_END
from src.models import Child, User
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.repositories.event_type import EventTypeRepository


class Dashboard:
    def __init__(
        self,
        child_repository: ChildRepository = Depends(ChildRepository),
        chart_repository: ChartRepository = Depends(ChartRepository),
        event_type_repository: EventTypeRepository = Depends(EventTypeRepository),
    ):
        self.child_repository = child_repository
        self.chart_repository = chart_repository
        self.event_type_repository = event_type_repository

    async def get_last_three_days(
        self,
        child_id: int,
        user: User,
        today: date = None,
    ):
        child = await self.child_repository.find(
            child_id, options=[selectinload(Child.users)]
        )

        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")

        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")

        # get sleep events for 3 days (today, yesterday, and the day before yesterday)
        event_type_ids = await self.event_type_repository.get_sleep_event_types(
            child.id
        )

        # day_before_yesterday_rows = await self.chart_repository.get_cycle_day_events(
        #     child, datetime.now(), event_type_ids
        # )
        # day_before_yesterday_rows = self.isolate_cycle_day_events(
        #     day_before_yesterday_rows
        # )

        if today is None:
            today = datetime.now().date()

        day_before_yesterday_date = today - timedelta(days=2)
        day_before_yesterday_rows = await self.chart_repository.get_cycle_day_events(
            child, day_before_yesterday_date, event_type_ids
        )
        day_before_yesterday_rows = self.isolate_cycle_day_events(
            day_before_yesterday_rows, day_before_yesterday_date, event_type_ids
        )

        yesterday_date = today - timedelta(days=1)
        yesterday_rows = await self.chart_repository.get_cycle_day_events(
            child, yesterday_date, event_type_ids
        )
        yesterday_rows = self.isolate_cycle_day_events(
            yesterday_rows, yesterday_date, event_type_ids
        )

        today_date = today
        today_rows_a = await self.chart_repository.get_cycle_day_events(
            child, today_date, event_type_ids
        )
        today_rows = self.isolate_cycle_day_events(
            today_rows_a, today_date, event_type_ids
        )

        return {
            "today": self.cycle_day_sleep_data(today_rows, event_type_ids),
            "yesterday": self.cycle_day_sleep_data(yesterday_rows, event_type_ids),
            "day_before_yesterday": self.cycle_day_sleep_data(
                day_before_yesterday_rows, event_type_ids
            ),
        }

    def cycle_day_sleep_data(self, rows: list[dict], event_type_ids: tuple):
        sleep_start_id, sleep_end_id = event_type_ids
        if len(rows) < 2:
            return {
                "day_sleeps": [],
                "night_sleeps": [],
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

        sum_data = self.calc_sleep_summary(rows, event_type_ids)
        # return day_sleeps
        return {
            "day_sleeps": day_sleeps,
            "night_sleeps": night_sleeps,
            "total_sleep_duration": sum_data["total_sleep"],
            "night_sleep_duration": sum_data["night_sleep"],
            "day_sleep_duration": sum_data["day_sleep"],
            "total_awake_duration": sum_data["total_awake"],
            "day_awake_duration": sum_data["day_awake"],
            "night_awake_duration": sum_data["night_awake"],
            "night_sleep_end": rows[-1]["occurred_at"] if rows else None,
            # "rows": rows,
        }

    def calc_sleep_summary(self, rows: list, event_types: tuple) -> dict:
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

            elif row["event_type_id"] == wake_id and asleep_at is not None:
                duration = (row["occurred_at"] - asleep_at).total_seconds()
                total_sleep += duration

                if DAY_START <= asleep_at.time() < DAY_END:
                    day_sleep += duration
                else:
                    night_sleep += duration

                asleep_at = None
                awake_at = row["occurred_at"]

        def fmt(seconds):
            hours, rem = divmod(seconds, 3600)
            minutes = rem // 60
            return f"{int(hours)}h {int(minutes)}m" if hours else f"{int(minutes)}m"

        return {
            "total_sleep": fmt(total_sleep),
            "night_sleep": fmt(night_sleep),
            "day_sleep": fmt(day_sleep),
            "total_awake": fmt(day_awake + night_awake),
            "day_awake": fmt(day_awake),
            "night_awake": fmt(night_awake),
        }

    def isolate_cycle_day_events(self, rows, day_date: date, event_type_ids: tuple):
        sleep_start_id, sleep_end_id = event_type_ids
        day_events = []
        earliest_start = None
        latest_event = None
        for row in rows:
            day_start_dt = datetime.combine(row["occurred_at"].date(), DAY_START)

            # continue
            if row["occurred_at"].date() == day_date:
                if (
                    row["event_type_id"] == sleep_start_id
                    and row["occurred_at"] < day_start_dt
                ):
                    continue
                if (
                    row["event_type_id"] == sleep_end_id
                    and row["occurred_at"] < day_start_dt
                ):
                    earliest_start = row["occurred_at"]
                    continue

                if (
                    row["event_type_id"] == sleep_start_id
                    and earliest_start is not None
                    and not day_events
                ):
                    day_events.append(
                        {"event_type_id": sleep_end_id, "occurred_at": earliest_start}
                    )
                    earliest_start = None

                day_events.append(
                    {
                        "event_type_id": row["event_type_id"],
                        "occurred_at": row["occurred_at"],
                    }
                )

            # если следующий день
            else:
                if row["occurred_at"] < day_start_dt:
                    # до старта дня точно записываем все события
                    day_events.append(
                        {
                            "event_type_id": row["event_type_id"],
                            "occurred_at": row["occurred_at"],
                        }
                    )
                    latest_event = {
                        "event_type_id": row["event_type_id"],
                        "occurred_at": row["occurred_at"],
                    }
                    continue

                if latest_event is None:
                    continue
                elif (
                    latest_event["event_type_id"] == sleep_start_id
                    and row["event_type_id"] == sleep_end_id
                ):
                    day_events.append(
                        {
                            "event_type_id": row["event_type_id"],
                            "occurred_at": row["occurred_at"],
                        }
                    )
                    latest_event = {
                        "event_type_id": row["event_type_id"],
                        "occurred_at": row["occurred_at"],
                    }
                    break

        return day_events
