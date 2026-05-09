from fastapi import Depends, HTTPException
from sqlalchemy.orm import selectinload

from src.models import Child, User
from src.repositories.child import ChildRepository


class ChildAccessGuard:
    def __init__(self, child_repository: ChildRepository = Depends(ChildRepository)):
        self.child_repository = child_repository

    async def assert_access(self, user: User, child_id: int) -> Child:
        child = await self.child_repository.find(child_id, options=[selectinload(Child.users)])
        if child is None:
            raise HTTPException(status_code=404, detail="Child not found")
        if not any(u.id == user.id for u in child.users):
            raise HTTPException(status_code=403, detail="Access denied")
        return child
