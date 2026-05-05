from src.constants.sleep import DAY_START


from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class _IsolationContext:
    day_start_dt: datetime
    sleep_start_id: int
    sleep_end_id: int
    events: list = field(default_factory=list)
    earliest_wake_up: datetime | None = None
    overnight_sleep_started: bool = False
    done: bool = False


class CycleDayEventsIsolator:
    def isolate(
        self,
        event_rows: list,
        day_date: date,
        event_type_ids: tuple,
    ) -> list[dict]:
        ctx = self._build_context(day_date, event_type_ids)

        for row in event_rows:
            is_target_date = row["occurred_at"].date() == day_date

            if is_target_date:
                self._process_target_date_row(row, ctx)
            else:
                self._process_other_date_row(row, ctx)

            if ctx.done:
                break

        return ctx.events

    @staticmethod
    def _build_context(day_date: date, event_type_ids: tuple) -> _IsolationContext:
        sleep_start_id, sleep_end_id = event_type_ids
        return _IsolationContext(
            day_start_dt=datetime.combine(day_date, DAY_START),
            sleep_start_id=sleep_start_id,
            sleep_end_id=sleep_end_id,
        )

    def _process_target_date_row(self, row: dict, ctx: _IsolationContext) -> None:
        event_type = row["event_type_id"]
        occurred_at = row["occurred_at"]
        is_before_day_start = occurred_at < ctx.day_start_dt

        if is_before_day_start:
            self._handle_before_day_start(event_type, occurred_at, ctx)
        else:
            self._handle_active_day_zone(event_type, occurred_at, ctx)

    def _handle_before_day_start(
        self,
        event_type: int,
        occurred_at: datetime,
        ctx: _IsolationContext,
    ) -> None:
        if event_type == ctx.sleep_end_id:
            ctx.earliest_wake_up = occurred_at

    def _handle_active_day_zone(
        self,
        event_type: int,
        occurred_at: datetime,
        ctx: _IsolationContext,
    ) -> None:
        had_early_wakeup = ctx.earliest_wake_up is not None
        day_not_started = not ctx.events
        is_sleep_start = event_type == ctx.sleep_start_id

        if is_sleep_start and had_early_wakeup and day_not_started:
            ctx.events.append(self.make_event(ctx.sleep_end_id, ctx.earliest_wake_up))
            ctx.earliest_wake_up = None

        ctx.events.append(self.make_event(event_type, occurred_at))

        if is_sleep_start:
            ctx.overnight_sleep_started = True

    def _process_other_date_row(self, row: dict, ctx: _IsolationContext) -> None:
        if not ctx.overnight_sleep_started:
            return

        event_type = row["event_type_id"]
        occurred_at = row["occurred_at"]

        if event_type != ctx.sleep_end_id:
            return

        ctx.events.append(self.make_event(event_type, occurred_at))
        ctx.done = True

    @staticmethod
    def make_event(event_type_id: int, occurred_at: datetime) -> dict:
        return {"event_type_id": event_type_id, "occurred_at": occurred_at}
