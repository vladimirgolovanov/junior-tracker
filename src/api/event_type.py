from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.auth.users import current_active_user
from src.models import User
from src.repositories.event_type import EventTypeRepository

router = APIRouter()

CurrentUser = Annotated[User, Depends(current_active_user)]


@router.get("/")
async def event_types(
    child_id: Annotated[int, Query()],
    user: CurrentUser,
    repo: EventTypeRepository = Depends(),
):
    return await repo.get(child_id=child_id)
