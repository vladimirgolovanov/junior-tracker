from pydantic import BaseModel


class Event(BaseModel):
    description: str


class EventCreate(Event):
    pass
