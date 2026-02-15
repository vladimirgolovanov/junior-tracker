from fastapi import APIRouter, Depends

from src.schemas.event import EventCreate
from src.services.event import EventService

router = APIRouter()


@router.post("/")
async def create_event(
    event: EventCreate,
    service: EventService = Depends(),
):
    return await service.create(event)
