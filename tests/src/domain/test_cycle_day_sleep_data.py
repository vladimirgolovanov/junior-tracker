import pytest
from datetime import datetime

from src.domain.services.cycle_day_sleep_data import CycleDaySleepData

SLEEP_ID = 1
WAKE_ID = 2
EVENT_TYPES = (SLEEP_ID, WAKE_ID)


def test_current_awake_when_child_is_awake():
    rows = [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 6, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 9, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 10, 30)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 3, 27, 12, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 3, 27, 13, 30)},
    ]
    current_time = datetime(2026, 3, 27, 17, 5)

    result = CycleDaySleepData().build(
        rows, EVENT_TYPES, is_today=True, current_time=current_time
    )

    assert result["total_awake_duration"] == 455
    assert result["day_awake_duration"] == 455
    assert result["current_awake"] == 215
    assert result["current_sleep"] == 0
