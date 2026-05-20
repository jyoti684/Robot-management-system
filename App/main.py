from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth, dashboard, logs, robot
from app.core.config import get_settings
from app.db import Base, SessionLocal, engine
from app.services.auth_service import AuthService

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        AuthService().ensure_default_commander(
            db,
            username=settings.default_commander_username,
            password=settings.default_commander_password,
        )
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(robot.router)
app.include_router(logs.router)
