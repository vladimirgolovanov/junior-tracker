from typing import Optional

from pydantic import AnyHttpUrl
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
    rabbitmq_tg_commands_queue: str = ""
    rabbitmq_tg_commands_responses_queue: str = ""
    rabbitmq_range_events_queue: str = ""
    rabbitmq_analytics_queue: str = ""
    sentry_dsn: str = ""
    token_lifetime_seconds: int = 60 * 60 * 24 * 14
    predict_url: Optional[AnyHttpUrl] = None


settings = Settings()
