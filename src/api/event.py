from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.auth.users import current_active_user
from src.models import User
from src.schemas.event import EventCreate, EventCreateInternal
from src.services.event import EventService
from src.services.rabbit_publisher import RabbitPublisher, get_publisher

router = APIRouter()

CurrentUser = Annotated[User, Depends(current_active_user)]


@router.get("/")
async def events(
    child_id: Annotated[int, Query()],
    user: CurrentUser,
    service: EventService = Depends(),
):
    return await service.get(user, child_id)


@router.post("/")
async def create_event(
    event: EventCreate,
    service: EventService = Depends(),
    publisher: RabbitPublisher | None = Depends(get_publisher),
):
    event_internal = EventCreateInternal(**event.model_dump())
    return await service.create(event_internal, publisher=publisher)
