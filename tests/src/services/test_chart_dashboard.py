import pytest
from datetime import datetime, timezone

from src.services.daily import TimelineService
from src.services.dashboard import Dashboard

rows_a = [
    {"event_type_id": 1, "occurred_at": "2026-03-14 00:05:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 06:50:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 10:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 11:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 13:50:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 14:35:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 14:45:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 15:35:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 18:45:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 05:45:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 07:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 08:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 10:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 12:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 15:10:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 16:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 19:00:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 22:55:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 23:05:00.000000"},
]
rows_b = [
    {"event_type_id": 1, "occurred_at": "2026-03-15 00:05:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 06:45:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 08:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 09:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 11:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 13:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 16:10:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 17:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 20:00:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 23:55:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 00:05:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 06:10:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 08:10:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 08:50:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 11:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 13:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 16:28:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 17:03:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 19:40:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 23:55:00.000000"},
]

rows_c = [
    {"event_type_id": 1, "occurred_at": "2026-03-16 01:05:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 07:10:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 09:10:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 09:50:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 12:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 14:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 17:28:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-16 18:03:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-16 20:40:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-17 00:55:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-17 09:40:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-17 10:55:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-17 13:40:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-17 14:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-17 16:50:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-17 18:00:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-17 20:45:00.000000"},
]


class TestChartDashboard:
    def test_isolate_cycle_day_events(self):
        rows = [
            {**row, "occurred_at": datetime.fromisoformat(row["occurred_at"])}
            for row in rows_c
        ]
        service = Dashboard()
        day_date = datetime(2026, 3, 16).date()
        pairs = service.isolate_cycle_day_events(rows, day_date)
        # echo pairs
        print("\n")
        # print(*pairs, sep="\n")
        # print(pairs[0]["occurred_at"])
        assert pairs[0]["occurred_at"] == datetime.fromisoformat(
            "2026-03-16 07:10:00.000000"
        )

    # def test_cycle_day_sleep_data(self):
    #     service = Dashboard()
    #     day_date = datetime(2026, 3, 14).date()
    #     day_rows = service.isolate_cycle_day_events(rows, day_date)
    #     pairs = service.cycle_day_sleep_data(day_rows)
    #     print(pairs)
