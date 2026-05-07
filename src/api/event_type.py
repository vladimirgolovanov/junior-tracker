from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.auth.users import current_active_user
from src.models import User
from src.schemas.event_type import EventTypeCreate, EventTypeUpdate
from src.services.event_type_extend_service import EventTypeExtendService

router = APIRouter()

CurrentUser = Annotated[User, Depends(current_active_user)]


@router.get("/formats")
async def event_type_formats():
    return ["range", "range_end", "plain", "described", "metric"]


@router.get("/")
async def event_types(
    child_id: Annotated[int, Query()],
    user: CurrentUser,
    service: EventTypeExtendService = Depends(),
):
    return await service.get_event_types(child_id=child_id)


@router.post("/")
async def create_event_type(
    body: EventTypeCreate,
    user: CurrentUser,
    service: EventTypeExtendService = Depends(),
):
    return await service.create(user, body)


@router.patch("/{event_type_id}")
async def update_event_type(
    event_type_id: int,
    body: EventTypeUpdate,
    user: CurrentUser,
    service: EventTypeExtendService = Depends(),
):
    return await service.update(user, event_type_id, body)
