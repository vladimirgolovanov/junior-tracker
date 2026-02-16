from fastapi import APIRouter, Depends

from src.auth.users import current_active_user
from src.api.event import router as event_router
from src.api.keys import router as keys_router
from src.api.device import router as device_router
from src.services.api_keys import get_api_key

router = APIRouter(prefix="/api")

router.include_router(
    router=event_router,
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(current_active_user)],
)

router.include_router(
    router=keys_router,
    prefix="/keys",
    tags=["keys"],
    dependencies=[Depends(current_active_user)],
)

router.include_router(
    router=device_router,
    prefix="/device",
    tags=["device"],
    dependencies=[Depends(get_api_key)],
)
