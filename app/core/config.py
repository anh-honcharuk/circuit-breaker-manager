from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Microservice Resilience Platform"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str
    redis_url: str

    celery_broker_url: str
    celery_result_backend: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    metrics_enabled: bool = True
    websocket_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()