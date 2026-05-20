from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class RobotTelemetry(BaseModel):
    battery_level: int = 100
    position_x: int = 0
    position_y: int = 0
    status: str = "idle"
    connection_status: str = "connected"
    latency_ms: int = 0
    signal_strength: str = "good"


class MoveCommand(BaseModel):
    direction: str = Field(pattern="^(up|down|left|right)$")
    steps: int = Field(default=1, ge=1, le=5)


class CommandResult(BaseModel):
    accepted: bool
    detail: str
    telemetry: RobotTelemetry | None = None
