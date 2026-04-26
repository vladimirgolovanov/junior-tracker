from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(
    settings.db_url,
    echo=settings.db_echo,
    echo_pool="debug",
    pool_size=3,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def db_session(
    session: AsyncSession = AsyncSession(),
) -> AsyncGenerator[AsyncSession, None]:
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
