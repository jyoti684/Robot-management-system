# Robot Management System (CMP9134)

A complete, self-contained Robot Management System comprising:

- **Dashboard service:** FastAPI, Jinja2, JavaScript, SQLAlchemy and SQLite.
- **Virtual Robot API:** a second FastAPI service with stateful telemetry and movement.
- **Security:** signed sessions, PBKDF2 password hashing and Viewer/Commander RBAC.
- **Reliability:** timeouts, bounded retries, Signal Lost state and audit logging.
- **Quality evidence:** PyTest suite, coverage configuration and GitHub Actions CI.
- **Deployment:** Dockerfiles and Docker Compose with health checks and startup ordering.

## 1. Required software

Install one of the following:

### Recommended
- Docker Desktop with Docker Compose v2.

### Native development alternative
- Python 3.12 or later.

## 2. Fastest start with Docker

1. Copy `.env.example` to `.env`.
2. Change the passwords and secret in `.env`.
3. Run:

```bash
docker compose up --build
```

4. Open: <http://localhost:8000>

The Virtual Robot API is available at <http://localhost:8001/docs>.

### Demonstration accounts

The defaults below are intended only for local assessment demonstration and can be changed in `.env`:

| Role | Username | Password |
|---|---|---|
| Commander | `commander` | `Commander123!` |
| Viewer | `viewer` | `Viewer123!` |

## 3. Windows one-click launch

Double-click:

```text
start_windows.bat
```

To stop the application, double-click `stop_windows.bat`.

## 4. Native Python start

### Linux/macOS

```bash
chmod +x start_native.sh
./start_native.sh
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Start-Process powershell -ArgumentList '-NoExit', '-Command', '.venv\Scripts\Activate.ps1; uvicorn virtual_robot.main:app --host 0.0.0.0 --port 8001'
$env:ROBOT_API_URL='http://127.0.0.1:8001'
uvicorn app.main:app --app-dir dashboard --host 0.0.0.0 --port 8000
```

## 5. Functional demonstration

1. Log in as **Viewer** and confirm telemetry is visible.
2. Confirm movement controls are disabled and a direct command returns HTTP 403.
3. Log out and log in as **Commander**.
4. Move the robot in all four directions using 1–5 steps.
5. Confirm position, battery, latency, connection state and mission logs update.
6. Simulate Virtual Robot failure:

```bash
python scripts/simulate_failure.py on
```

7. Confirm the dashboard displays **Signal Lost** and records a connection error.
8. Restore the service:

```bash
python scripts/simulate_failure.py off
```

9. Confirm the dashboard reconnects automatically.

## 6. Automated tests and coverage

```bash
python -m pytest --cov=dashboard/app --cov=virtual_robot --cov-report=term-missing --cov-fail-under=80
```

The suite covers authentication, RBAC, valid and invalid commands, telemetry mapping, retry exhaustion, degraded-state handling, logging, duplicate registration, logout and low-battery alerts.

## 7. Smoke test of a running deployment

After starting both services:

```bash
python scripts/smoke_test.py
```

The script verifies service health, Viewer restriction, Commander control and telemetry.

## 8. Main endpoints

### Dashboard
- `GET /health`
- `GET /login`
- `POST /login`
- `GET /register`
- `POST /register`
- `GET /dashboard`
- `GET /api/robot/telemetry`
- `POST /api/robot/command`
- `GET /api/logs`
- `POST /logout`

### Virtual Robot API
- `GET /health`
- `GET /telemetry`
- `POST /move`
- `POST /reset`
- `POST /admin/failure/{enabled}`

## 9. Repository evidence for resubmission

After uploading this project to GitHub:

1. Create Issues for Docker validation, CI, negative-path tests, security hardening, README/video and accessibility.
2. Work in named branches.
3. Use meaningful commits.
4. Open pull requests linked to Issues.
5. Merge only after the CI workflow passes.
6. Create release tag `v1.0.0`.
7. Add real screenshots and the demonstration-video link to the report appendix.

## 10. Security note

This is an academic prototype. Before public or production deployment, enable HTTPS, use a managed secret store, set secure cookie flags, remove default accounts, add CSRF protection, rate limiting, account lockout and a production database.
