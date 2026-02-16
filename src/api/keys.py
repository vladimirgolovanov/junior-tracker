from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.auth.users import current_active_user
from src.models import User
from src.models.api_key import APIKey

router = APIRouter()


@router.post("/api-keys")
async def create_api_key(
    name: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # todo: refactor
    api_key = APIKey(key=APIKey.generate_key(), name=name, user_id=user.id)
    db.add(api_key)
    await db.commit()
    return {"key": api_key.key, "name": api_key.name}
