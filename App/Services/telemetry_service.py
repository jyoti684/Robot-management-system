from typing import Protocol

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import MissionLog
from app.schemas import RobotTelemetry


class TelemetrySubscriber(Protocol):
    def update(self, telemetry: RobotTelemetry, db: Session) -> None: ...


class AuditTrailSubscriber:
    def update(self, telemetry: RobotTelemetry, db: Session) -> None:
        db.add(
            MissionLog(
                event_type="telemetry",
                robot_status=telemetry.status,
                battery_level=telemetry.battery_level,
                position_x=telemetry.position_x,
                position_y=telemetry.position_y,
                message=f"Telemetry received with {telemetry.connection_status} status",
            )
        )
        db.commit()


class AlertingSubscriber:
    def update(self, telemetry: RobotTelemetry, db: Session) -> None:
        settings = get_settings()
        if telemetry.battery_level <= settings.low_battery_threshold:
            db.add(
                MissionLog(
                    event_type="alert",
                    robot_status=telemetry.status,
                    battery_level=telemetry.battery_level,
                    position_x=telemetry.position_x,
                    position_y=telemetry.position_y,
                    message="Low battery threshold reached",
                )
            )
            db.commit()


class TelemetrySubject:
    def __init__(self) -> None:
        self._subscribers: list[TelemetrySubscriber] = []

    def attach(self, subscriber: TelemetrySubscriber) -> None:
        self._subscribers.append(subscriber)

    def notify(self, telemetry: RobotTelemetry, db: Session) -> None:
        for subscriber in self._subscribers:
            subscriber.update(telemetry, db)


def build_telemetry_subject() -> TelemetrySubject:
    subject = TelemetrySubject()
    subject.attach(AuditTrailSubscriber())
    subject.attach(AlertingSubscriber())
    return subject
