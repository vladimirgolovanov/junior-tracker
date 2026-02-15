from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "postgresql+asyncpg://app_user:app_password@localhost:54321/app_db"
    db_echo: bool = True


settings = Settings()
