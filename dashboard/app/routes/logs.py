from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import MissionLog, User, UserRole
from ..schemas import LogRecord
from ..security import require_role

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=list[LogRecord])
def logs(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(require_role(UserRole.VIEWER)),
    db: Session = Depends(get_db),
) -> list[MissionLog]:
    stmt = select(MissionLog).order_by(desc(MissionLog.timestamp)).limit(limit)
    return list(db.scalars(stmt).all())
