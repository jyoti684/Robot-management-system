from __future__ import annotations

from sqlalchemy import func, select

from app.db import SessionLocal
from app.main import app
from app.models import MissionLog
from app.services.robot_client import get_robot_client
from tests.conftest import FakeRobotClient


def test_unauthenticated_api_is_rejected(client):
    assert client.get("/api/robot/telemetry").status_code == 401
    assert client.get("/api/logs").status_code == 401


def test_viewer_can_monitor_but_cannot_command(client, login):
    assert login(client, "viewer", "Viewer123!").status_code == 303
    telemetry = client.get("/api/robot/telemetry")
    assert telemetry.status_code == 200
    assert telemetry.json()["connection_status"] == "connected"
    command = client.post("/api/robot/command", json={"direction": "up", "steps": 1})
    assert command.status_code == 403


def test_commander_command_is_logged(client, login):
    assert login(client, "commander", "Commander123!").status_code == 303
    response = client.post("/api/robot/command", json={"direction": "right", "steps": 3})
    assert response.status_code == 200
    assert response.json()["accepted"] is True
    with SessionLocal() as db:
        log = db.scalar(select(MissionLog).where(MissionLog.event_type == "command"))
        assert log is not None
        assert log.command_type == "right"
        assert log.position_x == 3


def test_invalid_command_payloads_return_422(client, login):
    login(client, "commander", "Commander123!")
    assert client.post("/api/robot/command", json={"direction": "diagonal", "steps": 1}).status_code == 422
    assert client.post("/api/robot/command", json={"direction": "up", "steps": 6}).status_code == 422


def test_telemetry_failure_returns_signal_lost_and_logs_error(client, login):
    app.dependency_overrides[get_robot_client] = lambda: FakeRobotClient(fail_telemetry=True)
    login(client, "viewer", "Viewer123!")
    response = client.get("/api/robot/telemetry")
    assert response.status_code == 200
    assert response.json()["connection_status"] == "signal_lost"
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(MissionLog).where(MissionLog.event_type == "connection_error"))
    assert count == 1


def test_command_failure_returns_503_and_logs_error(client, login):
    app.dependency_overrides[get_robot_client] = lambda: FakeRobotClient(fail_command=True)
    login(client, "commander", "Commander123!")
    response = client.post("/api/robot/command", json={"direction": "left", "steps": 2})
    assert response.status_code == 503
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(MissionLog).where(MissionLog.event_type == "command_error"))
    assert count == 1


def test_low_battery_creates_alert(client, login):
    app.dependency_overrides[get_robot_client] = lambda: FakeRobotClient(battery=20)
    login(client, "viewer", "Viewer123!")
    assert client.get("/api/robot/telemetry").status_code == 200
    with SessionLocal() as db:
        events = list(db.scalars(select(MissionLog.event_type)).all())
    assert "telemetry" in events
    assert "alert" in events
