import os

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, NullPool
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src import get_db
from src.models.base import Base

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://app_user:app_password@localhost:54321/test_db"
)

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)


# создаём таблицы один раз
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# connection для каждого теста
@pytest_asyncio.fixture
async def connection():

    async with test_engine.connect() as conn:
        transaction = await conn.begin()

        yield conn

        await transaction.rollback()


# session для теста
@pytest_asyncio.fixture
async def session(connection):

    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
    )

    yield session

    await session.close()


# override FastAPI dependency
@pytest_asyncio.fixture(autouse=True)
async def override_db(session):

    async def _get_test_db():
        yield session

    app.dependency_overrides[get_db] = _get_test_db

    yield

    app.dependency_overrides.clear()
