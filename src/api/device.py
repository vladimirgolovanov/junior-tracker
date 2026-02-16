from fastapi import APIRouter, Depends

from src.models.api_key import APIKey
from src.services.api_keys import get_api_key

router = APIRouter()


@router.get("/events")
async def events(api_key: APIKey = Depends(get_api_key)):
    return {"message": "Access granted via API key"}
