from __future__ import annotations

import os
import sys

import httpx


BASE = os.getenv("RMS_BASE_URL", "http://127.0.0.1:8000")


def assert_status(response: httpx.Response, expected: int, label: str) -> None:
    if response.status_code != expected:
        raise AssertionError(f"{label}: expected {expected}, got {response.status_code}: {response.text}")
    print(f"PASS: {label} ({expected})")


def main() -> int:
    with httpx.Client(base_url=BASE, follow_redirects=False, timeout=10) as client:
        assert_status(client.get("/health"), 200, "Dashboard health")
        assert_status(client.post("/login", data={"username": "viewer", "password": "Viewer123!"}), 303, "Viewer login")
        assert_status(client.get("/api/robot/telemetry"), 200, "Viewer telemetry")
        assert_status(client.post("/api/robot/command", json={"direction": "up", "steps": 1}), 403, "Viewer command rejected")
        client.post("/logout")
        assert_status(client.post("/login", data={"username": "commander", "password": "Commander123!"}), 303, "Commander login")
        result = client.post("/api/robot/command", json={"direction": "right", "steps": 2})
        assert_status(result, 200, "Commander command")
        if not result.json().get("accepted"):
            raise AssertionError("Commander command was not accepted")
        assert_status(client.get("/api/logs"), 200, "Mission logs")
    print("All smoke tests passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
