import re
from datetime import date, time

from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
    field_validator,
    model_validator,
)

# Strict "HH:MM" (exactly 5 chars): 00:00–23:59, zero-padded.
_HHMM_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _parse_hhmm(value: object) -> time | None:
    if value is None:
        return None
    if not isinstance(value, str) or not _HHMM_RE.match(value):
        raise ValueError("must be a string in 'HH:MM' format, e.g. '06:00'")
    hour, minute = (int(part) for part in value.split(":"))
    return time(hour=hour, minute=minute)


class ChildUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None
    birthday: date | None = None
    day_start: time | None = None
    day_end: time | None = None

    @field_validator("day_start", "day_end", mode="before")
    @classmethod
    def _validate_hhmm(cls, value: object) -> time | None:
        return _parse_hhmm(value)

    @model_validator(mode="after")
    def _both_or_neither(self) -> "ChildUpdate":
        if (self.day_start is None) != (self.day_end is None):
            raise ValueError("day_start and day_end must be provided together")
        return self


class ChildRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    tg_chat_id: str | None = None
    timezone: str | None = None
    birthday: date | None = None
    day_start: time | None = None
    day_end: time | None = None

    @field_serializer("day_start", "day_end")
    def _serialize_hhmm(self, value: time | None) -> str | None:
        return value.strftime("%H:%M") if value is not None else None
