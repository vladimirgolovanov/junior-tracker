from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="src/.env",
        env_file_encoding="utf-8",
    )

    db_url: str = ""
    db_echo: bool = False
    rabbit_url: str = ""
    queue_name: str = ""


settings = Settings()
