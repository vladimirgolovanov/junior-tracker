import pytest
from datetime import datetime, date, timezone

from src.models import User, Child, Event
from src.models.child import child_users
from src.models.event_type import EventType
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.repositories.event_type import EventTypeRepository
from src.services.dashboard import Dashboard

SCENARIO_1 = (
    {
        "user": {"email": "dash_test@test.com", "hashed_password": "x"},
        "child": {"name": "test baby", "timezone": "UTC"},
        "events": [
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 1, 16, 7, 30, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 1, 16, 10, 0, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 1, 16, 11, 0, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 1, 16, 19, 0, tzinfo=timezone.utc),
            },
        ],
    },
    date(2026, 1, 17),
    {
        # "total_sleep_duration": "1h 0m",
        # "night_sleep_duration": "0m",
        # "day_sleep_duration": "1h 0m",
        # "total_awake_duration": "8h 0m",
        "night_sleep_end": datetime(2026, 1, 16, 19, 0),
    },
)

SCENARIO_2 = (
    {
        "user": {"email": "dash_test2@test.com", "hashed_password": "x"},
        "child": {"name": "test baby 2", "timezone": "UTC"},
        "events": [
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 1, 19, 7, 0, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 1, 19, 9, 30, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 1, 19, 11, 0, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 1, 19, 13, 0, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 1, 19, 14, 30, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 1, 19, 19, 30, tzinfo=timezone.utc),
            },
        ],
    },
    date(2026, 1, 20),
    {
        # "total_sleep_duration": "3h 0m",
        # "night_sleep_duration": "0m",
        # "day_sleep_duration": "3h 0m",
        # "total_awake_duration": "7h 0m",
        "night_sleep_end": datetime(2026, 1, 19, 19, 30),
    },
)

SCENARIO_3 = (
    {
        "user": {"email": "dash_test3@test.com", "hashed_password": "x"},
        "child": {"name": "test baby 3", "timezone": "UTC"},
        "events": [
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 3, 27, 6, 20, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 3, 27, 8, 45, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 3, 27, 9, 20, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 3, 27, 12, 0, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 3, 27, 13, 40, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 3, 27, 17, 35, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 3, 27, 18, 5, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 3, 27, 20, 10, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 3, 27, 23, 55, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_start",
                "occurred_at": datetime(2026, 3, 28, 0, 5, tzinfo=timezone.utc),
            },
            {
                "type_name": "sleep_end",
                "occurred_at": datetime(2026, 3, 28, 6, 45, tzinfo=timezone.utc),
            },
        ],
    },
    date(2026, 3, 27),
    {
        "total_sleep_duration": "13h 10m",
        "night_sleep_duration": "3h 45m",
        "day_sleep_duration": "9h 25m",
        "total_awake_duration": "8h 50m",
        "night_sleep_end": datetime(2026, 3, 28, 6, 45),
    },
)


@pytest.mark.parametrize("seed, today, expected", [SCENARIO_3])
@pytest.mark.asyncio
async def test_dashboard_get_last_three_days(session, seed, today, expected):
    # --- seed user ---
    user = User(is_active=True, is_superuser=False, is_verified=True, **seed["user"])
    session.add(user)
    await session.flush()

    # --- seed child + child_user link ---
    child = Child(**seed["child"])
    session.add(child)
    await session.flush()
    await session.execute(
        child_users.insert().values(child_id=child.id, user_id=user.id, is_owner=True)
    )
    await session.flush()
    await session.refresh(child)

    # --- seed event types (always sleep_start + sleep_end pair) ---
    sleep_start_et = EventType(name="sleep_start", format="range", child_id=child.id)
    sleep_end_et = EventType(name="sleep_end", format="range", child_id=child.id)
    session.add_all([sleep_start_et, sleep_end_et])
    await session.flush()

    type_id_map = {"sleep_start": sleep_start_et.id, "sleep_end": sleep_end_et.id}

    # --- seed events ---
    for e in seed["events"]:
        session.add(
            Event(
                child_id=child.id,
                event_type_id=type_id_map[e["type_name"]],
                occurred_at=e["occurred_at"],
            )
        )
    await session.flush()

    # --- instantiate service directly (no FastAPI DI) ---
    service = Dashboard(
        child_repository=ChildRepository(db=session),
        chart_repository=ChartRepository(db=session),
        event_type_repository=EventTypeRepository(db=session),
    )

    # --- call service ---
    result = await service.get_last_three_days(child.id, user, today=today)

    # --- assert ---
    today = result["today"]
    for key, val in expected.items():
        assert today[key] == val, f"Mismatch on {key!r}: {today[key]!r} != {val!r}"
