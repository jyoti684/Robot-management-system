from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import MissionLog, User, UserRole
from ..schemas import CommandResult, MoveCommand, RobotTelemetry
from ..security import require_role
from ..services.robot_client import RobotAPIError, RobotClient, get_robot_client
from ..services.telemetry import build_telemetry_subject

router = APIRouter(prefix="/api/robot", tags=["robot"])


@router.get("/telemetry", response_model=RobotTelemetry)
async def telemetry(
    user: User = Depends(require_role(UserRole.VIEWER)),
    db: Session = Depends(get_db),
    client: RobotClient = Depends(get_robot_client),
) -> RobotTelemetry:
    try:
        result = await client.get_telemetry()
        build_telemetry_subject().notify(db, result, user.id)
        db.commit()
        return result
    except RobotAPIError as exc:
        degraded = RobotTelemetry(
            battery_level=0,
            position_x=0,
            position_y=0,
            status="unreachable",
            connection_status="signal_lost",
            latency_ms=0,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(
            MissionLog(
                event_type="connection_error",
                status=degraded.status,
                message=str(exc),
                user_id=user.id,
            )
        )
        db.commit()
        return degraded


@router.post("/command", response_model=CommandResult)
async def command(
    command_data: MoveCommand,
    user: User = Depends(require_role(UserRole.COMMANDER)),
    db: Session = Depends(get_db),
    client: RobotClient = Depends(get_robot_client),
) -> CommandResult:
    try:
        telemetry_result = await client.move_robot(command_data)
    except RobotAPIError as exc:
        db.add(
            MissionLog(
                event_type="command_error",
                command_type=command_data.direction,
                message=str(exc),
                user_id=user.id,
            )
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Robot API is unavailable; command was not executed",
        ) from exc

    db.add(
        MissionLog(
            event_type="command",
            command_type=command_data.direction,
            battery_level=telemetry_result.battery_level,
            position_x=telemetry_result.position_x,
            position_y=telemetry_result.position_y,
            status=telemetry_result.status,
            message=f"Executed {command_data.direction} for {command_data.steps} step(s)",
            user_id=user.id,
        )
    )
    db.commit()
    return CommandResult(accepted=True, message="Command executed", telemetry=telemetry_result)
