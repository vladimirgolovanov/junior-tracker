from datetime import date

from pydantic import BaseModel


class ChildUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None
    date_of_birth: date | None = None
