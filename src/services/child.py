from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db_helper import get_db
from src.models import Child, User
from src.repositories.child import ChildRepository
from src.schemas.child import ChildUpdate


class ChildService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        self.db = db
        self.repository = ChildRepository(db)

    async def get_by_chat_id(self, chat_id: str):
        return await self.repository.get_by_tg_chat_id(chat_id)

    async def update(self, user: User, child_id: int, data: ChildUpdate) -> Child:
        child = await self.repository.find(child_id, options=[selectinload(Child.users)])
        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")
        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")
        update_fields = data.model_dump(exclude_none=True)
        if not update_fields:
            return child
        return await self.repository.update(child_id, **update_fields)
