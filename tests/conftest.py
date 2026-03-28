import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, NullPool
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src import get_db
from src.auth.users import current_active_user
from src.models import User, Child
from src.models.base import Base
from src.models.child import child_users

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


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(session):
    user = User(
        email="test@example.com",
        hashed_password="fakehash",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_child(session, test_user):
    child = Child(name="test baby", timezone="UTC")
    session.add(child)
    await session.flush()
    await session.execute(
        child_users.insert().values(child_id=child.id, user_id=test_user.id, is_owner=True)
    )
    await session.flush()
    await session.refresh(child)
    return child


@pytest_asyncio.fixture
async def auth_override(test_user):
    app.dependency_overrides[current_active_user] = lambda: test_user
    yield
