from typing import AsyncGenerator, Optional

from fastapi import Depends, Request

from fastapi_users import BaseUserManager, IntegerIDMixin, FastAPIUsers
from fastapi_users.authentication import BearerTransport, AuthenticationBackend
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_helper import get_db
from src.default_event_types import DEFAULT_EVENT_TYPES
from src.models import User
from src.models.access_token import AccessToken
from src.models.child import Child, child_users
from src.models.event_type import EventType

SECRET = "SECRET"


get_async_session = get_db


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        session: AsyncSession = self.user_db.session

        child = Child(name="My Child")
        session.add(child)
        await session.flush()

        await session.execute(
            child_users.insert().values(
                child_id=child.id,
                user_id=user.id,
                is_owner=True,
            )
        )

        for template in DEFAULT_EVENT_TYPES:
            event_type = EventType(
                name=template["name"],
                keywords=template.get("keywords"),
                format=template["format"],
                color=template.get("color"),
                child_id=child.id,
            )
            session.add(event_type)

            if template["format"] == "range" and template.get("range_end"):
                await session.flush()
                end = template["range_end"]
                session.add(
                    EventType(
                        name=end["name"],
                        keywords=end.get("keywords"),
                        format="range_end",
                        color=end.get("color"),
                        child_id=child.id,
                        parent_id=event_type.id,
                    )
                )


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=60 * 60 * 24 * 14,
    )  # todo: config


bearer_transport = BearerTransport(tokenUrl="auth/login")

auth_backend = AuthenticationBackend(
    name="database",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_admin_user = fastapi_users.current_user(active=True, superuser=True)
