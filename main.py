from fastapi import FastAPI

from src.auth.users import fastapi_users, auth_backend
from src.schemas.user import UserRead, UserCreate
from src.api import router as api_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Junior!"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(api_router)
