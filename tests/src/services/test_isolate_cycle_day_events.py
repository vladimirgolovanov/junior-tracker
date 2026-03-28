import pytest
from datetime import datetime, date

from src.services.dashboard import Dashboard

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


@pytest.mark.parametrize("rows, day_date, expected", [SCENARIO_1, SCENARIO_2])
def test_isolate_cycle_day_events(rows, day_date, expected):
    service = Dashboard(
        child_repository=None, chart_repository=None, event_type_repository=None
    )
    result = service.isolate_cycle_day_events(rows, day_date)
    assert result == expected
