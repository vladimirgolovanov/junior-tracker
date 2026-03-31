from datetime import datetime, date

from src.constants.sleep import DAY_START


class CycleDayEventsIsolator:
    def isolate(self, rows: list, day_date: date, event_type_ids: tuple) -> list[dict]:
        sleep_start_id, sleep_end_id = event_type_ids
        day_events = []
        earliest_start = None
        latest_event = None
        for row in rows:
            day_start_dt = datetime.combine(row["occurred_at"].date(), DAY_START)

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

            else:
                if row["occurred_at"] < day_start_dt:
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
