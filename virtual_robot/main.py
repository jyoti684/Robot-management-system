from __future__ import annotations

import asyncio
import os
import random
from datetime import datetime, timezone
from threading import Lock
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Virtual Robot API", version="1.0.0")


class MoveRequest(BaseModel):
    direction: Literal["up", "down", "left", "right"]
    steps: int = Field(default=1, ge=1, le=5)


class RobotState:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.battery = float(os.getenv("ROBOT_INITIAL_BATTERY", "100"))
        self.status = "idle"
        self.failure_enabled = False
        self.lock = Lock()

    def reset(self) -> None:
        with self.lock:
            self.x = 0
            self.y = 0
            self.battery = float(os.getenv("ROBOT_INITIAL_BATTERY", "100"))
            self.status = "idle"
            self.failure_enabled = False


robot = RobotState()


def telemetry_payload() -> dict[str, object]:
    base_latency = int(os.getenv("ROBOT_LATENCY_MS", "75"))
    return {
        "battery_level": round(robot.battery, 1),
        "position_x": robot.x,
        "position_y": robot.y,
        "status": robot.status,
        "connection_status": "connected",
        "latency_ms": max(1, base_latency + random.randint(-12, 18)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def apply_latency() -> None:
    delay = max(0, int(os.getenv("ROBOT_LATENCY_MS", "75"))) / 1000
    await asyncio.sleep(delay)


def ensure_available() -> None:
    if robot.failure_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Simulated robot failure")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "virtual-robot"}


@app.get("/telemetry")
async def telemetry() -> dict[str, object]:
    ensure_available()
    await apply_latency()
    with robot.lock:
        return telemetry_payload()


@app.post("/move")
async def move(command: MoveRequest) -> dict[str, object]:
    ensure_available()
    await apply_latency()
    with robot.lock:
        robot.status = "moving"
        delta = command.steps
        if command.direction == "up":
            robot.y = min(10, robot.y + delta)
        elif command.direction == "down":
            robot.y = max(-10, robot.y - delta)
        elif command.direction == "left":
            robot.x = max(-10, robot.x - delta)
        else:
            robot.x = min(10, robot.x + delta)
        robot.battery = max(0.0, robot.battery - (0.6 * command.steps))
        robot.status = "idle" if robot.battery > 0 else "battery_depleted"
        return {"accepted": True, "message": "Movement completed", "telemetry": telemetry_payload()}


@app.post("/reset")
def reset() -> dict[str, object]:
    robot.reset()
    return {"reset": True, "telemetry": telemetry_payload()}


@app.post("/admin/failure/{enabled}")
def set_failure(enabled: bool, x_admin_token: str = Header(default="")) -> dict[str, bool]:
    expected = os.getenv("ROBOT_ADMIN_TOKEN", "demo-admin-token")
    if x_admin_token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")
    robot.failure_enabled = enabled
    return {"failure_enabled": robot.failure_enabled}
