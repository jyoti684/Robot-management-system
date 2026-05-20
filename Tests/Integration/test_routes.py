from app.models import User, UserRole
from app.security import hash_password


class FakeRobotClient:
    async def get_telemetry(self):
        from app.schemas import RobotTelemetry

        return RobotTelemetry(
            battery_level=80,
            position_x=1,
            position_y=2,
            status="idle",
            connection_status="connected",
            latency_ms=99,
            signal_strength="good",
        )

    async def move_robot(self, command):
        from app.schemas import RobotTelemetry

        return RobotTelemetry(
            battery_level=78,
            position_x=1,
            position_y=3,
            status=f"moving_{command.direction}",
            connection_status="connected",
            latency_ms=100,
            signal_strength="good",
        )


def _login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 401


def test_viewer_can_fetch_telemetry_but_not_command(client, db_session, monkeypatch):
    viewer = User(username="viewer1", password_hash=hash_password("Password123"), role=UserRole.viewer)
    db_session.add(viewer)
    db_session.commit()

    from app.api.routes import robot as robot_routes

    monkeypatch.setattr(robot_routes, "get_robot_client", lambda: FakeRobotClient())

    _login(client, "viewer1", "Password123")
    telem = client.get("/api/robot/telemetry")
    assert telem.status_code == 200
    blocked = client.post("/api/robot/command", json={"direction": "up", "steps": 1})
    assert blocked.status_code == 403


def test_commander_can_issue_command(client, db_session, monkeypatch):
    commander = User(username="cmdr", password_hash=hash_password("Password123"), role=UserRole.commander)
    db_session.add(commander)
    db_session.commit()

    from app.api.routes import robot as robot_routes

    monkeypatch.setattr(robot_routes, "get_robot_client", lambda: FakeRobotClient())

    _login(client, "cmdr", "Password123")
    response = client.post("/api/robot/command", json={"direction": "up", "steps": 1})
    assert response.status_code == 200
    assert response.json()["accepted"] is True
