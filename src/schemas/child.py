from pydantic import BaseModel


class ChildUpdate(BaseModel):
    name: str | None = None
    timezone: str | None = None
