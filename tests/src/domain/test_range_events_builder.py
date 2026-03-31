import pytest
from datetime import datetime

from src.domain.services.range_events_builder import RangeEventsBuilder

SLEEP_ID = 1
WAKE_ID = 2
EVENT_TYPES = (SLEEP_ID, WAKE_ID)


# Normal start/end pair on the same day
SCENARIO_SIMPLE_PAIR = (
    [
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 21, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 1, 16, 23, 0)},
    ],
    [
        {
            "day": "2026-01-16",
            "start": datetime(2026, 1, 16, 21, 0),
            "end": datetime(2026, 1, 16, 23, 0),
        },
    ],
)

# Sleep crosses midnight — should split into two segments
SCENARIO_MIDNIGHT_CROSSING = (
    [
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 22, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 1, 17, 6, 0)},
    ],
    [
        {
            "day": "2026-01-16",
            "start": datetime(2026, 1, 16, 22, 0),
            "end": datetime(2026, 1, 17, 0, 0),
        },
        {
            "day": "2026-01-17",
            "start": datetime(2026, 1, 17, 0, 0),
            "end": datetime(2026, 1, 17, 6, 0),
        },
    ],
)

# End event with no preceding start — uses start-of-day as start
SCENARIO_END_WITHOUT_START = (
    [
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 1, 16, 7, 30)},
    ],
    [
        {
            "day": "2026-01-16",
            "start": datetime(2026, 1, 16, 0, 0),
            "end": datetime(2026, 1, 16, 7, 30),
        }
    ],
)

# Start event with no following end — caps at end-of-day (23:59:59)
SCENARIO_START_WITHOUT_END = (
    [
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 20, 0)},
    ],
    [
        {
            "day": "2026-01-16",
            "start": datetime(2026, 1, 16, 20, 0),
            "end": datetime(2026, 1, 16, 23, 59, 59),
        }
    ],
)

# Two starts in a row — first is capped at end-of-day, second starts a new segment
SCENARIO_TWO_STARTS = (
    [
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 20, 0)},
        {"event_type_id": SLEEP_ID, "occurred_at": datetime(2026, 1, 16, 22, 0)},
        {"event_type_id": WAKE_ID, "occurred_at": datetime(2026, 1, 17, 6, 0)},
    ],
    [
        {
            "day": "2026-01-16",
            "start": datetime(2026, 1, 16, 20, 0),
            "end": datetime(2026, 1, 16, 23, 59, 59),
        },
        {
            "day": "2026-01-16",
            "start": datetime(2026, 1, 16, 22, 0),
            "end": datetime(2026, 1, 17, 0, 0),
        },
        {
            "day": "2026-01-17",
            "start": datetime(2026, 1, 17, 0, 0),
            "end": datetime(2026, 1, 17, 6, 0),
        },
    ],
)

# Empty input
SCENARIO_EMPTY = ([], [])


@pytest.mark.parametrize(
    "rows, expected",
    [
        SCENARIO_SIMPLE_PAIR,
        SCENARIO_MIDNIGHT_CROSSING,
        SCENARIO_END_WITHOUT_START,
        SCENARIO_START_WITHOUT_END,
        SCENARIO_TWO_STARTS,
        SCENARIO_EMPTY,
    ],
)
def test_range_events_builder(rows, expected):
    result = RangeEventsBuilder().build(rows, EVENT_TYPES)
    assert result == expected
