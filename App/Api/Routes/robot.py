from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import MissionLog, User, UserRole
from app.schemas import CommandResult, MoveCommand, RobotTelemetry
from app.security import get_current_user, require_role
from app.services.robot_client import RobotAPIError, get_robot_client
from app.services.telemetry_service import build_telemetry_subject

router = APIRouter(prefix="/api/robot", tags=["robot"])
telemetry_subject = build_telemetry_subject()


@router.get("/telemetry", response_model=RobotTelemetry)
async def get_telemetry(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = get_robot_client()
    try:
        telemetry = await client.get_telemetry()
        telemetry_subject.notify(telemetry, db)
        return telemetry
    except RobotAPIError as exc:
        db.add(
            MissionLog(
                event_type="connection_error",
                user_id=user.id,
                message=f"Telemetry fetch failed: {exc}",
            )
        )
        db.commit()
        return RobotTelemetry(connection_status="signal_lost", status="unreachable")


@router.post("/command", response_model=CommandResult)
async def send_command(
    command: MoveCommand,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.commander)),
):
    client = get_robot_client()
    try:
        telemetry = await client.move_robot(command)
        db.add(
            MissionLog(
                event_type="command",
                command_type=command.direction,
                user_id=user.id,
                robot_status=telemetry.status,
                battery_level=telemetry.battery_level,
                position_x=telemetry.position_x,
                position_y=telemetry.position_y,
                message=f"Command {command.direction} executed for {command.steps} step(s)",
            )
        )
        db.commit()
        return CommandResult(accepted=True, detail="Command executed", telemetry=telemetry)
    except RobotAPIError as exc:
        db.add(
            MissionLog(
                event_type="command_error",
                command_type=command.direction,
                user_id=user.id,
                message=f"Command failed: {exc}",
            )
        )
        db.commit()
        raise HTTPException(status_code=503, detail="Robot API unavailable")
