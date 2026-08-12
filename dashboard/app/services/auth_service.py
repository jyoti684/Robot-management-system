from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import User, UserRole
from ..security import hash_password, verify_password


class DuplicateUsernameError(ValueError):
    pass


class AuthService:
    @staticmethod
    def register_viewer(db: Session, username: str, password: str) -> User:
        cleaned = username.strip().lower()
        if len(cleaned) < 3:
            raise ValueError("Username must contain at least three characters")
        user = User(username=cleaned, password_hash=hash_password(password), role=UserRole.VIEWER.value)
        db.add(user)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise DuplicateUsernameError("Username already exists") from exc
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        stmt = select(User).where(User.username == username.strip().lower(), User.is_active.is_(True))
        user = db.scalar(stmt)
        if user and verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    def ensure_account(db: Session, username: str, password: str, role: UserRole) -> User:
        cleaned = username.strip().lower()
        existing = db.scalar(select(User).where(User.username == cleaned))
        if existing:
            return existing
        user = User(username=cleaned, password_hash=hash_password(password), role=role.value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
