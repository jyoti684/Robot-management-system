from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.security import hash_password, verify_password


class AuthService:
    def register_viewer(self, db: Session, username: str, password: str) -> User:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("Username already exists")

        user = User(username=username, password_hash=hash_password(password), role=UserRole.viewer)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
        if not user:
            return None
        return user if verify_password(password, user.password_hash) else None

    def ensure_default_commander(self, db: Session, username: str, password: str) -> None:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return
        commander = User(username=username, password_hash=hash_password(password), role=UserRole.commander)
        db.add(commander)
        db.commit()
