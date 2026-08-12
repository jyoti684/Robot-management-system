from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import settings
from ..models import User
from ..security import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@router.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/login")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: User = Depends(get_current_user)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "poll_ms": int(settings.telemetry_poll_seconds * 1000),
        },
    )
