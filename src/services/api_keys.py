from datetime import datetime

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src import get_db
from src.models.api_key import APIKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key: str = Security(api_key_header), db: AsyncSession = Depends(get_db)
) -> APIKey:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key required"
        )

    result = await db.execute(
        select(APIKey)
        .options(selectinload(APIKey.child))
        .where(APIKey.key == api_key, APIKey.is_active == True)
    )
    key = result.scalar_one_or_none()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )

    # Обновить last_used
    key.last_used = datetime.now()
    await db.commit()

    return key
