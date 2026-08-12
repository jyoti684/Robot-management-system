from __future__ import annotations

import asyncio

import httpx
import pytest

from app.schemas import MoveCommand
from app.services.robot_client import RobotAPIError, RobotClient


@pytest.mark.asyncio
async def test_robot_client_maps_alias_fields():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "battery": 74,
                "x": 4,
                "y": -2,
                "status": "idle",
                "connection_status": "connected",
                "latency_ms": 31,
                "timestamp": "2026-08-05T10:00:00+00:00",
            },
        )

    client = RobotClient(base_url="http://robot.test", transport=httpx.MockTransport(handler))
    telemetry = await client.get_telemetry()
    assert telemetry.battery_level == 74
    assert telemetry.position_x == 4
    assert telemetry.position_y == -2


@pytest.mark.asyncio
async def test_robot_client_move_reads_nested_telemetry():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(
            200,
            json={
                "accepted": True,
                "telemetry": {
                    "battery_level": 90,
                    "position_x": 0,
                    "position_y": 2,
                    "status": "idle",
                    "connection_status": "connected",
                    "latency_ms": 25,
                    "timestamp": "2026-08-05T10:00:00+00:00",
                },
            },
        )

    client = RobotClient(base_url="http://robot.test", transport=httpx.MockTransport(handler))
    telemetry = await client.move_robot(MoveCommand(direction="up", steps=2))
    assert telemetry.position_y == 2


@pytest.mark.asyncio
async def test_robot_client_retries_then_raises():
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("offline", request=request)

    async def no_sleep(_: float) -> None:
        await asyncio.sleep(0)

    client = RobotClient(
        base_url="http://robot.test",
        max_attempts=3,
        transport=httpx.MockTransport(handler),
        sleep_func=no_sleep,
    )
    with pytest.raises(RobotAPIError, match="after 3 attempts"):
        await client.get_telemetry()
    assert calls == 3
