from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.auth.users import current_active_user
from src.models import User, Child
from src.schemas.child import ChildUpdate
from src.services.child import ChildService

router = APIRouter()


@router.get("/")
async def children(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Child).join(Child.users).where(User.id == user.id))
    return result.scalars().all()


@router.patch("/{child_id}")
async def update_child(
    child_id: int,
    body: ChildUpdate,
    user: User = Depends(current_active_user),
    service: ChildService = Depends(),
):
    return await service.update(user, child_id, body)
