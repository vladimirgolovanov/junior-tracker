import pytest
from datetime import datetime, timezone

from sqlalchemy import text

from src.models import Child
from src.models.event_type import EventType
from src.models.event import Event


@pytest.mark.asyncio
async def test_chart_returns_data(client, session, test_child, auth_override):
    # Seed event types
    sleep_start = EventType(name="sleep_start", child_id=test_child.id, format="range")
    sleep_end = EventType(name="sleep_end", child_id=test_child.id, format="range")
    session.add_all([sleep_start, sleep_end])
    await session.flush()

    # Seed events on 2026-01-15 UTC
    session.add_all([
        Event(
            child_id=test_child.id,
            event_type_id=sleep_start.id,
            occurred_at=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
        ),
        Event(
            child_id=test_child.id,
            event_type_id=sleep_end.id,
            occurred_at=datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc),
        ),
    ])
    await session.flush()

    resp = await client.get(
        "/api/chart/",
        params={
            "child_id": test_child.id,
            "date_from": "2026-01-15",
            "date_to": "2026-01-15",
            "event_type_ids": [sleep_start.id, sleep_end.id],
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["day"] == "2026-01-15"


@pytest.mark.asyncio
async def test_dashboard_returns_data(client, session, test_child, auth_override):
    # Seed sleep event types
    sleep_start = EventType(name="sleep_start", child_id=test_child.id, format="range")
    sleep_end = EventType(name="sleep_end", child_id=test_child.id, format="range")
    session.add_all([sleep_start, sleep_end])
    await session.flush()

    # today=2026-01-22 → yesterday_date = 2026-01-15
    # Seed events on 2026-01-15 that produce a valid cycle day
    session.add_all([
        Event(
            child_id=test_child.id,
            event_type_id=sleep_end.id,
            occurred_at=datetime(2026, 1, 15, 7, 30, tzinfo=timezone.utc),
        ),
        Event(
            child_id=test_child.id,
            event_type_id=sleep_start.id,
            occurred_at=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
        ),
        Event(
            child_id=test_child.id,
            event_type_id=sleep_end.id,
            occurred_at=datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc),
        ),
    ])
    await session.flush()

    resp = await client.get(
        "/api/chart/dashboard",
        params={"child_id": test_child.id, "today": "2026-01-22"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "yesterday" in data
    assert "total_sleep_duration" in data["yesterday"]
