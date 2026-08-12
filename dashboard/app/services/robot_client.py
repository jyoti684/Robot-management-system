from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import Any

import httpx

from ..config import settings
from ..schemas import MoveCommand, RobotTelemetry


class RobotAPIError(RuntimeError):
    pass


class RobotCommandFactory:
    @staticmethod
    def create_payload(command: MoveCommand) -> dict[str, Any]:
        return {"direction": command.direction, "steps": command.steps}


class RobotClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout_seconds: float = 5.0,
        max_attempts: int = 3,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep_func: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.base_url = (base_url or settings.robot_api_url).rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds, connect=min(2.0, timeout_seconds))
        self.max_attempts = max_attempts
        self.transport = transport
        self.sleep_func = sleep_func

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                async with httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout,
                    transport=self.transport,
                ) as client:
                    response = await client.request(method, path, **kwargs)
                    response.raise_for_status()
                    data = response.json()
                    if not isinstance(data, dict):
                        raise RobotAPIError("Robot API returned a non-object payload")
                    return data
            except (httpx.HTTPError, ValueError, RobotAPIError) as exc:
                last_error = exc
                if attempt < self.max_attempts:
                    await self.sleep_func(0.15 * (2 ** (attempt - 1)))
        raise RobotAPIError(f"Robot API request failed after {self.max_attempts} attempts: {last_error}")

    async def get_telemetry(self) -> RobotTelemetry:
        data = await self._request("GET", "/telemetry")
        return self._map_telemetry(data)

    async def move_robot(self, command: MoveCommand) -> RobotTelemetry:
        payload = RobotCommandFactory.create_payload(command)
        data = await self._request("POST", "/move", json=payload)
        if "telemetry" in data and isinstance(data["telemetry"], dict):
            data = data["telemetry"]
        return self._map_telemetry(data)

    @staticmethod
    def _map_telemetry(data: dict[str, Any]) -> RobotTelemetry:
        battery = data.get("battery_level", data.get("battery", 0))
        x = data.get("position_x", data.get("x", 0))
        y = data.get("position_y", data.get("y", 0))
        return RobotTelemetry(
            battery_level=float(battery),
            position_x=int(x),
            position_y=int(y),
            status=str(data.get("status", "unknown")),
            connection_status=str(data.get("connection_status", "connected")),
            latency_ms=int(data.get("latency_ms", 0)),
            timestamp=data.get("timestamp"),
        )


@lru_cache(maxsize=1)
def get_robot_client() -> RobotClient:
    return RobotClient()
