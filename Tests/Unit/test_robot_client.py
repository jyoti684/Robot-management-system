import httpx
import pytest

from app.schemas import MoveCommand
from app.services.robot_client import RobotClient


@pytest.mark.asyncio
async def test_get_telemetry_maps_payload(monkeypatch):
    client = RobotClient()

    async def fake_request(self, method, endpoint, **kwargs):
        return {"battery": 72, "x": 3, "y": 4, "status": "idle"}, 120

    monkeypatch.setattr(RobotClient, "_request", fake_request)
    telemetry = await client.get_telemetry()

    assert telemetry.battery_level == 72
    assert telemetry.position_x == 3
    assert telemetry.position_y == 4
    assert telemetry.connection_status == "connected"


@pytest.mark.asyncio
async def test_move_robot_sends_factory_payload(monkeypatch):
    client = RobotClient()
    captured = {}

    async def fake_request(self, method, endpoint, **kwargs):
        captured["json"] = kwargs["json"]
        return {"battery_level": 65, "position_x": 2, "position_y": 5, "status": "moving"}, 85

    monkeypatch.setattr(RobotClient, "_request", fake_request)
    telemetry = await client.move_robot(MoveCommand(direction="up", steps=2))

    assert captured["json"] == {"direction": "up", "steps": 2}
    assert telemetry.position_y == 5
