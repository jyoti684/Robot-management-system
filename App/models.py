from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserRole(str, Enum):
    viewer = "viewer"
    commander = "commander"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.viewer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    logs: Mapped[list["MissionLog"]] = relationship(back_populates="user")


class MissionLog(Base):
    __tablename__ = "mission_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    command_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    robot_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    battery_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User | None] = relationship(back_populates="logs")
