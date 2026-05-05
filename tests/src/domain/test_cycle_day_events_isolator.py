import pytest
from datetime import datetime, date

from src.domain.services.cycle_day_events_isolator import CycleDayEventsIsolator

SCENARIO_1 = (
    [
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 7, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 10, 0)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 11, 0)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 19, 0)},
    ],
    date(2026, 1, 16),
    [
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 7, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 10, 0)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 11, 0)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 19, 0)},
    ],
)

SCENARIO_2 = (
    [
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 6, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 9, 0)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 10, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 19, 0)},
    ],
    date(2026, 1, 16),
    [
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 6, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 9, 0)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 1, 16, 10, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 1, 16, 19, 0)},
    ],
)

SCENARIO_3 = (
    [
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 0, 50)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 4, 6, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 8, 45)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 4, 9, 55)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 13, 40)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 4, 14, 50)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 19, 35)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 5, 7, 0)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 5, 9, 20)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 5, 10, 45)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 5, 14, 30)},
    ],
    date(2026, 5, 4),
    [
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 4, 6, 30)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 8, 45)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 4, 9, 55)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 13, 40)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 4, 14, 50)},
        {"event_type_id": 1, "occurred_at": datetime(2026, 5, 4, 19, 35)},
        {"event_type_id": 2, "occurred_at": datetime(2026, 5, 5, 7, 0)},
    ],
)


@pytest.mark.parametrize(
    "rows, day_date, expected", [SCENARIO_1, SCENARIO_2, SCENARIO_3]
)
def test_cycle_day_events_isolator(rows, day_date, expected):
    result = CycleDayEventsIsolator().isolate(rows, day_date, (1, 2))
    assert result == expected
