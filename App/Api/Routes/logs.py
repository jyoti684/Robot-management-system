from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import MissionLog
from app.security import get_current_user

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
def list_logs(limit: int = 20, db: Session = Depends(get_db), _=Depends(get_current_user)):
    logs = db.query(MissionLog).order_by(MissionLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "timestamp": log.timestamp.isoformat(),
            "event_type": log.event_type,
            "command_type": log.command_type,
            "robot_status": log.robot_status,
            "battery_level": log.battery_level,
            "position": [log.position_x, log.position_y],
            "message": log.message,
        }
        for log in logs
    ]
