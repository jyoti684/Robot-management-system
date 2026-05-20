from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, UserRole

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user


def require_role(required_role: UserRole):
    def checker(user: User = Depends(get_current_user)) -> User:
        role_hierarchy = {UserRole.viewer: 1, UserRole.commander: 2}
        if role_hierarchy[user.role] < role_hierarchy[required_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker
