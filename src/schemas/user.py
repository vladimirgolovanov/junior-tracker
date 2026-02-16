from pydantic import BaseModel
from fastapi_users import schemas


class User(BaseModel):
    email: str
    password: str
    name: str


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
