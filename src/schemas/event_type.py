from typing import Literal

from pydantic import BaseModel

EventTypeFormat = Literal["range", "range_end", "plain", "described", "metric"]


class EventTypeCreate(BaseModel):
    child_id: int
    name: str
    format: EventTypeFormat
    color: str | None = None
    keywords: list[str] | None = None


class EventTypeUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    keywords: list[str] | None = None
