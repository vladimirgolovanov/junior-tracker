from datetime import datetime

from pydantic import BaseModel


class Event(BaseModel):
    description: str | None = None
    child_id: int
    event_type_id: int
    occurred_at: datetime
    volume: int | None = None


class EventCreate(Event):
    pass


class EventCreateInternal(EventCreate):
    pass  # todo: remove
