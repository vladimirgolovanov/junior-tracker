import contextvars
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import settings
from src.db_helper import async_session_maker
from src.models.access_token import AccessToken
from src.models.user import User

_current_user: contextvars.ContextVar[User | None] = contextvars.ContextVar(
    "mcp_current_user", default=None
)


def get_current_user() -> User:
    user = _current_user.get()
    if user is None:
        raise RuntimeError("No authenticated user in context")
    return user


class MCPBearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        token_str = auth_header.removeprefix("Bearer ").strip()
        max_age = datetime.now(timezone.utc) - timedelta(
            seconds=settings.token_lifetime_seconds
        )

        async with async_session_maker() as session:
            result = await session.execute(
                select(AccessToken).where(
                    AccessToken.token == token_str,
                    AccessToken.created_at >= max_age,
                )
            )
            access_token = result.scalar_one_or_none()

            if access_token is None:
                return JSONResponse(
                    {"detail": "Invalid or expired token"}, status_code=401
                )

            user_result = await session.execute(
                select(User).where(
                    User.id == access_token.user_id,
                    User.is_active.is_(True),
                )
            )
            user = user_result.scalar_one_or_none()

        if user is None:
            return JSONResponse(
                {"detail": "User not found or inactive"}, status_code=401
            )

        token = _current_user.set(user)
        try:
            response = await call_next(request)
        finally:
            _current_user.reset(token)

        return response
