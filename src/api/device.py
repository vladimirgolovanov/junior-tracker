from fastapi import APIRouter, Depends

from src.models.api_key import APIKey
from src.services.api_keys import get_api_key
from src.services.event import EventService

router = APIRouter()


@router.get("/last_sleep_start")
async def events(
    api_key: APIKey = Depends(get_api_key),
    service: EventService = Depends(),
):
    child_id = APIKey.child_id
    return await service.get(child_id)


# todo: last awake start
# todo: last food
