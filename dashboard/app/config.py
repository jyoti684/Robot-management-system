from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    robot_api_url: str = os.getenv("ROBOT_API_URL", "http://127.0.0.1:8001")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./rms.db")
    secret_key: str = os.getenv("SECRET_KEY", "development-only-change-me")
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    commander_username: str = os.getenv("COMMANDER_USERNAME", "commander")
    commander_password: str = os.getenv("COMMANDER_PASSWORD", "Commander123!")
    viewer_username: str = os.getenv("VIEWER_USERNAME", "viewer")
    viewer_password: str = os.getenv("VIEWER_PASSWORD", "Viewer123!")
    telemetry_poll_seconds: float = float(os.getenv("TELEMETRY_POLL_SECONDS", "2"))
    low_battery_threshold: float = float(os.getenv("LOW_BATTERY_THRESHOLD", "25"))


settings = Settings()
