from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Direction = Literal["up", "down", "left", "right"]


class MoveCommand(BaseModel):
    direction: Direction
    steps: int = Field(default=1, ge=1, le=5)


class RobotTelemetry(BaseModel):
    battery_level: float = Field(ge=0, le=100)
    position_x: int
    position_y: int
    status: str
    connection_status: str
    latency_ms: int = Field(ge=0)
    timestamp: datetime


class CommandResult(BaseModel):
    accepted: bool
    message: str
    telemetry: RobotTelemetry | None = None


class LogRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    event_type: str
    command_type: str | None
    battery_level: float | None
    position_x: int | None
    position_y: int | None
    status: str | None
    message: str
    user_id: int | None
