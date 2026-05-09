from datetime import datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException

from src.auth.users import current_active_user
from src.models import User
from src.schemas.event import EventCreate, EventCreateInternal, EventUpdate
from src.services.event import EventService
from src.services.rabbit_publisher import RabbitPublisher, get_publisher

router = APIRouter()

CurrentUser = Annotated[User, Depends(current_active_user)]


@router.get("/")
async def events(
    child_id: Annotated[int, Query()],
    user: CurrentUser,
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
    service: EventService = Depends(),
):
    if date_to is not None:
        if date_to.time() == time.min:
            date_to = datetime.combine(date_to.date(), time.max)

    return await service.get(
        user,
        child_id,
        occurred_at__gte=date_from,
        occurred_at__lte=date_to,
    )


@router.patch("/{event_id}")
async def update_event(
    event_id: int,
    data: EventUpdate,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    service: EventService = Depends(),
    publisher: RabbitPublisher | None = Depends(get_publisher),
):
    event = await service.update(
        event_id,
        data,
        user=user,
        publisher=publisher,
        background_tasks=background_tasks,
    )
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    service: EventService = Depends(),
    publisher: RabbitPublisher | None = Depends(get_publisher),
):
    deleted = await service.delete(
        event_id, user=user, publisher=publisher, background_tasks=background_tasks
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")


@router.post("/")
async def create_event(
    event: EventCreate,
    background_tasks: BackgroundTasks,
    service: EventService = Depends(),
    publisher: RabbitPublisher | None = Depends(get_publisher),
):
    event_internal = EventCreateInternal(**event.model_dump())
    return await service.create(
        event_internal, publisher=publisher, background_tasks=background_tasks
    )
