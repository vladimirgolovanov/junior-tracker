import pytest
from datetime import datetime

from src.domain.services.sleep_summary_calculator import SleepSummaryCalculator

SLEEP_ID = 1
WAKE_ID = 2
EVENT_TYPES = (SLEEP_ID, WAKE_ID)

SCENARIO_1 = (
    [
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 10, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 1, 16, 11, 0)},
    ],
    {
        "total_sleep": "1h 0m",
        "day_sleep": "1h 0m",
        "night_sleep": "0m",
        "total_awake": "0m",
        "day_awake": "0m",
        "night_awake": "0m",
    },
)

SCENARIO_2 = (
    [
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 20, 30)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 1, 17, 6, 30)},
    ],
    {
        "total_sleep": "10h 0m",
        "night_sleep": "10h 0m",
        "day_sleep": "0m",
        "total_awake": "0m",
        "day_awake": "0m",
        "night_awake": "0m",
    },
)

SCENARIO_3 = (
    [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 6, 20)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 8, 45)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 9, 20)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 12, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 13, 40)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 17, 35)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 18, 5)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 20, 10)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 23, 55)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 28, 0, 5)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 28, 6, 45)},
    ],
    {
        "total_sleep": "13h 10m",
        "day_sleep": "2h 45m",
        "night_sleep": "10h 25m",
        "total_awake": "11h 15m",
        "day_awake": "11h 5m",
        "night_awake": "10m",
    },
)


@pytest.mark.parametrize("rows, expected", [SCENARIO_1, SCENARIO_2, SCENARIO_3])
def test_sleep_summary_calculator(rows, expected):
    result = SleepSummaryCalculator().calculate(rows, EVENT_TYPES)
    assert result == expected
