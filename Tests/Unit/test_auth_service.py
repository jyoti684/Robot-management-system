from app.models import UserRole
from app.services.auth_service import AuthService


def test_register_viewer_creates_viewer_role(db_session):
    service = AuthService()
    user = service.register_viewer(db_session, "alice", "SuperSecure123")
    assert user.role == UserRole.viewer
    assert user.username == "alice"


def test_authenticate_returns_user_when_password_matches(db_session):
    service = AuthService()
    service.register_viewer(db_session, "bob", "SuperSecure123")
    user = service.authenticate(db_session, "bob", "SuperSecure123")
    assert user is not None
    assert user.username == "bob"
