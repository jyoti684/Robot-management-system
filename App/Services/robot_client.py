import asyncio
import time
from functools import lru_cache

import httpx

from app.core.config import get_settings
from app.schemas import MoveCommand, RobotTelemetry


class RobotAPIError(Exception):
    pass


class RobotCommandFactory:
    @staticmethod
    def create_payload(command: MoveCommand) -> dict:
        return {"direction": command.direction, "steps": command.steps}


class RobotClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.robot_api_base_url.rstrip("/")
        self.timeout = httpx.Timeout(5.0, connect=2.0)

    async def _request(self, method: str, endpoint: str, **kwargs):
        retries = 3
        delay = 0.4
        last_exc = None
        start = time.perf_counter()

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                    response = await client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                latency_ms = int((time.perf_counter() - start) * 1000)
                return response.json(), latency_ms
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                if attempt == retries:
                    break
                await asyncio.sleep(delay * attempt)

        raise RobotAPIError(str(last_exc))

    async def get_telemetry(self) -> RobotTelemetry:
        payload, latency_ms = await self._request("GET", self.settings.robot_telemetry_endpoint)
        return RobotTelemetry(
            battery_level=int(payload.get("battery_level", payload.get("battery", 100))),
            position_x=int(payload.get("position_x", payload.get("x", 0))),
            position_y=int(payload.get("position_y", payload.get("y", 0))),
            status=str(payload.get("status", "idle")),
            connection_status="connected",
            latency_ms=latency_ms,
            signal_strength="weak" if latency_ms > 2000 else "good",
        )

    async def move_robot(self, command: MoveCommand) -> RobotTelemetry:
        payload, latency_ms = await self._request(
            "POST",
            self.settings.robot_move_endpoint,
            json=RobotCommandFactory.create_payload(command),
        )
        return RobotTelemetry(
            battery_level=int(payload.get("battery_level", payload.get("battery", 100))),
            position_x=int(payload.get("position_x", payload.get("x", 0))),
            position_y=int(payload.get("position_y", payload.get("y", 0))),
            status=str(payload.get("status", "moving")),
            connection_status="connected",
            latency_ms=latency_ms,
            signal_strength="weak" if latency_ms > 2000 else "good",
        )


@lru_cache
def get_robot_client() -> RobotClient:
    return RobotClient()
