from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from sqlalchemy.orm import Session

from ..config import settings
from ..models import MissionLog
from ..schemas import RobotTelemetry


class TelemetrySubscriber(Protocol):
    def update(self, db: Session, telemetry: RobotTelemetry, user_id: int | None) -> None: ...


@dataclass
class TelemetrySubject:
    subscribers: list[TelemetrySubscriber] = field(default_factory=list)

    def attach(self, subscriber: TelemetrySubscriber) -> None:
        self.subscribers.append(subscriber)

    def notify(self, db: Session, telemetry: RobotTelemetry, user_id: int | None) -> None:
        for subscriber in self.subscribers:
            subscriber.update(db, telemetry, user_id)


class AuditTrailSubscriber:
    def update(self, db: Session, telemetry: RobotTelemetry, user_id: int | None) -> None:
        db.add(
            MissionLog(
                event_type="telemetry",
                battery_level=telemetry.battery_level,
                position_x=telemetry.position_x,
                position_y=telemetry.position_y,
                status=telemetry.status,
                message=f"Telemetry received; signal={telemetry.connection_status}",
                user_id=user_id,
            )
        )


class AlertingSubscriber:
    def update(self, db: Session, telemetry: RobotTelemetry, user_id: int | None) -> None:
        if telemetry.battery_level <= settings.low_battery_threshold:
            db.add(
                MissionLog(
                    event_type="alert",
                    battery_level=telemetry.battery_level,
                    position_x=telemetry.position_x,
                    position_y=telemetry.position_y,
                    status=telemetry.status,
                    message=f"Low battery: {telemetry.battery_level:.1f}%",
                    user_id=user_id,
                )
            )


def build_telemetry_subject() -> TelemetrySubject:
    subject = TelemetrySubject()
    subject.attach(AuditTrailSubscriber())
    subject.attach(AlertingSubscriber())
    return subject
