from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .db import Base, SessionLocal, engine
from .models import UserRole
from .routes import auth, dashboard, logs, robot
from .services.auth_service import AuthService


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        AuthService.ensure_account(
            db, settings.commander_username, settings.commander_password, UserRole.COMMANDER
        )
        AuthService.ensure_account(db, settings.viewer_username, settings.viewer_password, UserRole.VIEWER)
    yield


app = FastAPI(
    title="Robot Management System",
    version="1.0.0",
    description="CMP9134 executable Robot Ground Control Station",
    lifespan=lifespan,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    same_site="lax",
    https_only=settings.cookie_secure,
    max_age=60 * 60 * 8,
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(robot.router)
app.include_router(logs.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "rms-dashboard"}
