from __future__ import annotations

from fastapi.testclient import TestClient

from virtual_robot.main import app, robot


def make_client() -> TestClient:
    robot.reset()
    return TestClient(app)


def test_virtual_robot_health_and_telemetry():
    with make_client() as client:
        assert client.get("/health").status_code == 200
        telemetry = client.get("/telemetry")
        assert telemetry.status_code == 200
        assert telemetry.json()["connection_status"] == "connected"


def test_virtual_robot_move_updates_position_and_battery():
    with make_client() as client:
        before = client.get("/telemetry").json()
        result = client.post("/move", json={"direction": "right", "steps": 2})
        assert result.status_code == 200
        after = result.json()["telemetry"]
        assert after["position_x"] == 2
        assert after["battery_level"] < before["battery_level"]


def test_virtual_robot_rejects_invalid_steps():
    with make_client() as client:
        assert client.post("/move", json={"direction": "up", "steps": 6}).status_code == 422


def test_virtual_robot_failure_switch_requires_token_and_recovers():
    with make_client() as client:
        denied = client.post("/admin/failure/true", headers={"X-Admin-Token": "wrong"})
        assert denied.status_code == 403
        enabled = client.post("/admin/failure/true", headers={"X-Admin-Token": "demo-admin-token"})
        assert enabled.status_code == 200
        assert client.get("/telemetry").status_code == 503
        disabled = client.post("/admin/failure/false", headers={"X-Admin-Token": "demo-admin-token"})
        assert disabled.status_code == 200
        assert client.get("/telemetry").status_code == 200
