from datetime import date

from pydantic import BaseModel
from fastapi_users import schemas

from src.schemas.event_type import EventTypeFormat


class User(BaseModel):
    email: str
    password: str
    name: str


class UserRead(schemas.BaseUser[int]):
    pass


class EventTypeRangeEndRegistration(BaseModel):
    name: str
    keywords: list[str] | None = None
    color: str | None = None


class EventTypeRegistration(BaseModel):
    name: str
    format: EventTypeFormat
    keywords: list[str] | None = None
    color: str | None = None
    range_end: EventTypeRangeEndRegistration | None = None


class UserCreate(schemas.BaseUserCreate):
    child_name: str | None = None
    timezone: str | None = None
    date_of_birth: date | None = None
    event_types: list[EventTypeRegistration] | None = None  # None → use defaults

    def create_update_dict(self):
        d = super().create_update_dict()
        for key in ("child_name", "timezone", "date_of_birth", "event_types"):
            d.pop(key, None)
        return d

    def create_update_dict_superuser(self):
        d = super().create_update_dict_superuser()
        for key in ("child_name", "timezone", "date_of_birth", "event_types"):
            d.pop(key, None)
        return d


class UserUpdate(schemas.BaseUserUpdate):
    pass
