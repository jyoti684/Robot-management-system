from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.security import get_current_user

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": request.query_params.get("error")},
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "grid_size": settings.grid_size,
            "low_battery_threshold": settings.low_battery_threshold,
            "poll_interval_seconds": settings.poll_interval_seconds,
        },
    )
