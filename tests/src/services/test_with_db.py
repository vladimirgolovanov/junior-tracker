import sys
from datetime import datetime, timezone

import pytest
from sqlalchemy import select, text

from src.models import Event, Child
from src.services.event import EventService
from src.services.tg_msg_parser import TgMsgParser


@pytest.mark.asyncio
async def test_with_db(session):
    child = Child(name="test child")
    session.add(child)
    await session.commit()

    result = await session.execute(
        text(
            "INSERT INTO event_types (name, child_id, keywords, format, parent_id) VALUES (:name, :child_id, :keywords, :format, :parent_id) RETURNING id"
        ),
        {
            "name": "sleep_start",
            "child_id": child.id,
            "keywords": ["sleep"],
            "format": "range",
            "parent_id": None,
        },
    )
    sleep_start_id = result.scalar_one()

    await session.commit()
    result = await session.execute(
        text(
            "INSERT INTO event_types (name, child_id, keywords, format, parent_id) VALUES (:name, :child_id, :keywords, :format, :parent_id) RETURNING id"
        ),
        {
            "name": "sleep_end",
            "child_id": child.id,
            "keywords": None,
            "format": "range_end",
            "parent_id": sleep_start_id,
        },
    )
    await session.commit()
    sleep_end_id = result.scalar_one()

    event_types = [
        {
            "type": "range",
            "event_type_id": (sleep_start_id, sleep_end_id),
            "keywords": ["sleep"],
        }
    ]

    result = await session.execute(select(Child))
    children = result.scalars().all()

    assert len(children) == 1
    assert children[0].name == "test child"

    event_service = EventService(session)

    parser = TgMsgParser(event_types)
    timestamp = datetime(2025, 2, 2, tzinfo=timezone.utc)

    range_line = "10:00-"
    events = parser.parse_entry(range_line, timestamp, child.id, "Europe/London", 1)
    for event in events:
        await event_service.update_or_create(event, len(events))
        await session.commit()
    await session.commit()

    db_events = await event_service.get(child.id)

    assert len(db_events) == 1
    assert db_events[0].event_type_id == sleep_start_id
    assert db_events[0].occurred_at == datetime(2025, 2, 2, 10, 0, tzinfo=timezone.utc)

    edited_range_line = "10:00-10:30 sleep"
    events = parser.parse_entry(
        edited_range_line, timestamp, child.id, "Europe/London", 1
    )
    for event in events:
        print(vars(event))

    for event in events:
        await event_service.update_or_create(event, len(events))
        await session.commit()
    db_events = await event_service.get(child.id)
    assert len(db_events) == 2
