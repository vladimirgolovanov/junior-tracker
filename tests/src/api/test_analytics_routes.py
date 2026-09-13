import pytest
from datetime import datetime, timezone

from src.models.event_type import EventType
from src.models.event import Event


async def _seed_formula_events(session, test_child):
    """Seed a formula event type and events (child timezone is UTC).

    Volumes/dates are chosen to span two ISO weeks and two months:
      2026-08-10 (Mon) vol 100  \\ same ISO week
      2026-08-12 (Wed) vol  50  /
      2026-08-17 (Mon) vol 200    own ISO week
      2026-09-02 (Wed) vol  30  \\ ISO week starting Mon 2026-08-31
      2026-09-03 (Thu) vol  20  /
    """
    formula = EventType(name="formula", child_id=test_child.id, format="metric")
    session.add(formula)
    await session.flush()

    session.add_all([
        Event(child_id=test_child.id, event_type_id=formula.id, volume=100,
              occurred_at=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)),
        Event(child_id=test_child.id, event_type_id=formula.id, volume=50,
              occurred_at=datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)),
        Event(child_id=test_child.id, event_type_id=formula.id, volume=200,
              occurred_at=datetime(2026, 8, 17, 12, 0, tzinfo=timezone.utc)),
        Event(child_id=test_child.id, event_type_id=formula.id, volume=30,
              occurred_at=datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)),
        Event(child_id=test_child.id, event_type_id=formula.id, volume=20,
              occurred_at=datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)),
    ])
    await session.flush()


@pytest.mark.asyncio
async def test_formula_default_is_per_day(client, session, test_child, auth_override):
    await _seed_formula_events(session, test_child)

    resp = await client.get(
        "/api/analytics/formula",
        params={
            "child_id": test_child.id,
            "date_from": "2026-08-01",
            "date_to": "2026-09-30",
        },
    )

    assert resp.status_code == 200
    assert resp.json() == [
        {"date": "2026-08-10", "total_volume": 100, "count": 1},
        {"date": "2026-08-12", "total_volume": 50, "count": 1},
        {"date": "2026-08-17", "total_volume": 200, "count": 1},
        {"date": "2026-09-02", "total_volume": 30, "count": 1},
        {"date": "2026-09-03", "total_volume": 20, "count": 1},
    ]


@pytest.mark.asyncio
async def test_formula_granularity_day_matches_default(
    client, session, test_child, auth_override
):
    await _seed_formula_events(session, test_child)

    resp = await client.get(
        "/api/analytics/formula",
        params={
            "child_id": test_child.id,
            "date_from": "2026-08-01",
            "date_to": "2026-09-30",
            "granularity": "day",
        },
    )

    assert resp.status_code == 200
    assert resp.json() == [
        {"date": "2026-08-10", "total_volume": 100, "count": 1},
        {"date": "2026-08-12", "total_volume": 50, "count": 1},
        {"date": "2026-08-17", "total_volume": 200, "count": 1},
        {"date": "2026-09-02", "total_volume": 30, "count": 1},
        {"date": "2026-09-03", "total_volume": 20, "count": 1},
    ]


@pytest.mark.asyncio
async def test_formula_granularity_week(client, session, test_child, auth_override):
    await _seed_formula_events(session, test_child)

    resp = await client.get(
        "/api/analytics/formula",
        params={
            "child_id": test_child.id,
            "date_from": "2026-08-01",
            "date_to": "2026-09-30",
            "granularity": "week",
        },
    )

    assert resp.status_code == 200
    # Buckets keyed by Monday of the ISO week.
    assert resp.json() == [
        {"date": "2026-08-10", "total_volume": 150, "count": 2},
        {"date": "2026-08-17", "total_volume": 200, "count": 1},
        {"date": "2026-08-31", "total_volume": 50, "count": 2},
    ]


@pytest.mark.asyncio
async def test_formula_granularity_month(client, session, test_child, auth_override):
    await _seed_formula_events(session, test_child)

    resp = await client.get(
        "/api/analytics/formula",
        params={
            "child_id": test_child.id,
            "date_from": "2026-08-01",
            "date_to": "2026-09-30",
            "granularity": "month",
        },
    )

    assert resp.status_code == 200
    # Buckets keyed by the first day of the month.
    assert resp.json() == [
        {"date": "2026-08-01", "total_volume": 350, "count": 3},
        {"date": "2026-09-01", "total_volume": 50, "count": 2},
    ]


@pytest.mark.asyncio
async def test_formula_invalid_granularity_returns_422(
    client, session, test_child, auth_override
):
    resp = await client.get(
        "/api/analytics/formula",
        params={
            "child_id": test_child.id,
            "date_from": "2026-08-01",
            "date_to": "2026-09-30",
            "granularity": "bogus",
        },
    )

    assert resp.status_code == 422
