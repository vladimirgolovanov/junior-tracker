from contextlib import asynccontextmanager

import aio_pika
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from src.auth.users import fastapi_users, auth_backend
from src.schemas.user import UserRead, UserCreate
from src.api import router as api_router
from src.config import settings

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.rabbit_url:
        app.state.rabbit_connection = await aio_pika.connect_robust(settings.rabbit_url)
    else:
        app.state.rabbit_connection = None
    yield
    if app.state.rabbit_connection:
        await app.state.rabbit_connection.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


@app.get("/")
def root():
    return ""


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(api_router)
