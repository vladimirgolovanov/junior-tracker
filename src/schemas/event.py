from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Event(BaseModel):
    description: str | None = None
    child_id: int
    event_type_id: int
    occurred_at: datetime
    volume: int | None = None
    tg_message_id: int | None = None


class EventRead(BaseModel):
    id: int
    description: str | None = None
    volume: int | None = None
    # Naive datetime in the child's local timezone (no offset).
    occurred_at: datetime
    tg_message_id: int | None = None
    child_id: int
    event_type_id: int

    model_config = ConfigDict(from_attributes=True)


class EventCreate(Event):
    pass


class EventCreateInternal(EventCreate):
    pass  # todo: remove


class EventUpdate(BaseModel):
    occurred_at: datetime | None = None
    volume: int | None = None
    description: str | None = None
