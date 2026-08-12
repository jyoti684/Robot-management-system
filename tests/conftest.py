from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
sys.path.insert(0, str(ROOT))

TEST_DB = ROOT / ".test_rms.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["COMMANDER_USERNAME"] = "commander"
os.environ["COMMANDER_PASSWORD"] = "Commander123!"
os.environ["VIEWER_USERNAME"] = "viewer"
os.environ["VIEWER_PASSWORD"] = "Viewer123!"

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import UserRole  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402
from app.services.robot_client import get_robot_client  # noqa: E402


class FakeRobotClient:
    def __init__(self, *, fail_telemetry: bool = False, fail_command: bool = False, battery: float = 80.0):
        self.fail_telemetry = fail_telemetry
        self.fail_command = fail_command
        self.battery = battery

    async def get_telemetry(self):
        from datetime import datetime, timezone
        from app.schemas import RobotTelemetry
        from app.services.robot_client import RobotAPIError

        if self.fail_telemetry:
            raise RobotAPIError("simulated telemetry failure")
        return RobotTelemetry(
            battery_level=self.battery,
            position_x=2,
            position_y=3,
            status="idle",
            connection_status="connected",
            latency_ms=40,
            timestamp=datetime.now(timezone.utc),
        )

    async def move_robot(self, command):
        from datetime import datetime, timezone
        from app.schemas import RobotTelemetry
        from app.services.robot_client import RobotAPIError

        if self.fail_command:
            raise RobotAPIError("simulated command failure")
        x = command.steps if command.direction == "right" else 0
        y = command.steps if command.direction == "up" else 0
        return RobotTelemetry(
            battery_level=self.battery - 1,
            position_x=x,
            position_y=y,
            status="idle",
            connection_status="connected",
            latency_ms=55,
            timestamp=datetime.now(timezone.utc),
        )


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        AuthService.ensure_account(db, "commander", "Commander123!", UserRole.COMMANDER)
        AuthService.ensure_account(db, "viewer", "Viewer123!", UserRole.VIEWER)
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    app.dependency_overrides[get_robot_client] = lambda: FakeRobotClient()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def login():
    def _login(client: TestClient, username: str, password: str):
        return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)
    return _login
