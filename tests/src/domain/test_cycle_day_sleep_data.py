import pytest
from datetime import datetime

from src.domain.services.cycle_day_sleep_data import CycleDaySleepData

SLEEP_ID = 1
WAKE_ID = 2
EVENT_TYPES = (SLEEP_ID, WAKE_ID)

SCENARIO_1 = (
    [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 6, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 9, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 10, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 12, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 13, 30)},
    ],
    datetime(2026, 3, 27, 17, 5),
    {
        "total_awake_duration": 455,
        "day_awake_duration": 455,
        "current_awake": 215,
        "current_sleep": 0,
    },
    True,
)

SCENARIO_2 = (
    [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 6, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 9, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 10, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 12, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 13, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 16, 55)},
    ],
    datetime(2026, 3, 27, 17, 5),
    {
        "total_awake_duration": 445,
        "day_awake_duration": 445,
        "current_awake": 0,
        "current_sleep": 10,
    },
    True,
)

SCENARIO_3 = (
    [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 7, 55)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 9, 20)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 10, 45)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 13, 30)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 14, 5)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 18, 5)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 18, 35)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 19, 50)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 28, 6, 40)},
    ],
    datetime(2026, 3, 28, 7, 10),
    {
        # "day_sleeps": ,
        # "night_sleeps",
        "total_sleep_duration": 800,
        "night_sleep_duration": 650,
        "day_sleep_duration": 150,
        "night_awake_duration": 0,
        "day_awake_duration": 565,
        "total_awake_duration": 565,
        "night_sleep_end": datetime(2026, 3, 28, 6, 40),
        # "total_awake_duration": 445,
        # "day_awake_duration": 445,
        # "current_awake": 0,
        # "current_sleep": 10,
    },
    False,
)

SCENARIO_4 = (
    [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 5, 4, 6, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 5, 4, 8, 45)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 5, 4, 9, 55)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 5, 4, 13, 40)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 5, 4, 14, 50)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 5, 4, 19, 35)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 5, 5, 7, 0)},
    ],
    datetime(2026, 5, 5, 7, 10),
    {
        "segments": [
            {
                "time": 135,
                "start": "06:30",
                "end": "08:45",
                "segment_type": "day_awake",
            },
            {"time": 70, "start": "08:45", "end": "09:55", "segment_type": "day_sleep"},
            {
                "time": 225,
                "start": "09:55",
                "end": "13:40",
                "segment_type": "day_awake",
            },
            {"time": 70, "start": "13:40", "end": "14:50", "segment_type": "day_sleep"},
            {
                "time": 285,
                "start": "14:50",
                "end": "19:35",
                "segment_type": "day_awake",
            },
            {
                "time": 685,
                "start": "19:35",
                "end": "07:00",
                "segment_type": "night_sleep",
            },
        ],
    },
    False,
)


@pytest.mark.parametrize(
    "rows, current_time, expected, is_today",
    [SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4],
)
def test_current_awake_when_child_is_awake(rows, current_time, expected, is_today):
    result = CycleDaySleepData().build(
        rows, EVENT_TYPES, is_today=is_today, current_time=current_time
    )

    for field, value in expected.items():
        assert result[field] == value, f"{field}: expected {value}, got {result[field]}"
