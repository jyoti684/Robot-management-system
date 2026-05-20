# Robot Ground Control Station (FastAPI)

A web-based dashboard for monitoring and commanding a virtual autonomous robot through a REST API. This repository is structured to satisfy the coursework requirement for a **Robot Management System** with telemetry monitoring, command control, RBAC, audit logging, graceful error handling, Docker support, automated tests, and CI/CD.

## Features

- **Robot API integration** via HTTP using a dedicated `RobotClient`
- **Live telemetry dashboard** with battery, position, status, latency, and signal state
- **2D grid map** showing robot position in real time
- **Secure authentication** with password hashing and session-based login
- **Role-Based Access Control**:
  - `viewer`: telemetry and logs only
  - `commander`: telemetry, logs, and movement commands
- **Persistent audit trail** using SQLite + SQLAlchemy
- **Resilience to connection issues** with retry logic and non-blocking UI behaviour
- **Software engineering practices**:
  - OOP service layer
  - Singleton-style cached robot client
  - Factory for command payload creation
  - Observer-style telemetry subscribers for audit and alert logging
- **Automated tests** (unit + integration)
- **GitHub Actions CI**
- **Docker / docker-compose** deployment

## Project Structure

```text
robot_gcs_project/
├── app/
│   ├── api/routes/          # HTTP routes and web pages
│   ├── core/                # configuration
│   ├── services/            # robot client, telemetry subject, auth logic
│   ├── static/              # CSS and browser JavaScript
│   ├── templates/           # Jinja2 templates
│   ├── db.py                # SQLAlchemy setup
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # DB models
│   ├── schemas.py           # Pydantic DTOs
│   └── security.py          # auth and RBAC helpers
├── tests/
│   ├── unit/
│   └── integration/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update values if needed.
4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open `http://localhost:8000`

## Default Commander Account

The application seeds a default commander on first startup using the configured environment variables.

- Username: `commander`
- Password: `ChangeThisPassword123!`

Change these before submitting or deploying.

## Docker Setup

> Replace the placeholder `robot-api` image in `docker-compose.yml` with the actual container image provided on Blackboard.

```bash
docker compose up --build
```

The dashboard will be available at `http://localhost:8000`.

## Assumed Robot API Contract

Because the exact Blackboard API specification is not included here, this scaffold assumes:

- `GET /telemetry` → returns JSON with battery and coordinates
- `POST /move` → accepts `{ "direction": "up", "steps": 1 }`
- `GET /health` → optional health endpoint

The `RobotClient` is intentionally isolated so you can adapt endpoint names or payload shapes in a single file once the final API documentation is released.

## Testing

Run all tests:

```bash
pytest --cov=app --cov-report=term-missing
```

## Recommended GitHub Evidence for Submission

Upload this full repository and show evidence of:

- meaningful commits over time
- Issues / Kanban board for feature-driven development
- CI pipeline passing
- test coverage runs
- Docker build and application startup

## Report / Video Alignment

This codebase is designed to support your report sections on:

- architecture and design patterns
- project planning and risk mitigation
- testing and containerisation
- social / ethical implications of robotic control systems
- AI verification log entries for code generation, review, and modification
