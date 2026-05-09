from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.models import Child, User
from src.repositories.child import ChildRepository
from src.schemas.child import ChildUpdate
from src.services.child_access import ChildAccessGuard


class ChildService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        child_guard: ChildAccessGuard = Depends(ChildAccessGuard),
    ):
        self.db = db
        self.repository = ChildRepository(db)
        self.child_guard = child_guard

    async def get_by_chat_id(self, chat_id: str):
        return await self.repository.get_by_tg_chat_id(chat_id)

    async def update(self, user: User, child_id: int, data: ChildUpdate) -> Child:
        child = await self.child_guard.assert_access(user, child_id)
        update_fields = data.model_dump(exclude_none=True)
        if not update_fields:
            return child
        return await self.repository.update(child_id, **update_fields)
