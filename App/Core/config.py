from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Robot Ground Control Station"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./robot_gcs.db"
    robot_api_base_url: str = "http://robot-api:8001"
    robot_telemetry_endpoint: str = "/telemetry"
    robot_move_endpoint: str = "/move"
    robot_health_endpoint: str = "/health"
    poll_interval_seconds: int = 2
    grid_size: int = 10
    low_battery_threshold: int = 25
    default_commander_username: str = "commander"
    default_commander_password: str = "ChangeThisPassword123!"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
