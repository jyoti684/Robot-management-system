from __future__ import annotations

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import User
from app.security import hash_password, verify_password


def test_password_hash_round_trip():
    encoded = hash_password("SecurePass123!")
    assert encoded != "SecurePass123!"
    assert verify_password("SecurePass123!", encoded)
    assert not verify_password("wrong-password", encoded)


def test_invalid_login_returns_401(client):
    response = client.post("/login", data={"username": "viewer", "password": "wrong"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.text


def test_viewer_registration_and_duplicate_rejection(client):
    first = client.post(
        "/register", data={"username": "newviewer", "password": "NewViewer123!"}, follow_redirects=False
    )
    assert first.status_code == 303
    duplicate = client.post("/register", data={"username": "newviewer", "password": "NewViewer123!"})
    assert duplicate.status_code == 400
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(User).where(User.username == "newviewer"))
    assert count == 1


def test_logout_invalidates_session(client, login):
    assert login(client, "viewer", "Viewer123!").status_code == 303
    assert client.get("/api/logs").status_code == 200
    assert client.post("/logout", follow_redirects=False).status_code == 303
    assert client.get("/api/logs").status_code == 401
