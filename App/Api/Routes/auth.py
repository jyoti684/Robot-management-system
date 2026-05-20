from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
auth_service = AuthService()


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = auth_service.register_viewer(db, username=username, password=password)
        request.session["user_id"] = user.id
        return RedirectResponse(url="/dashboard", status_code=303)
    except ValueError:
        return RedirectResponse(url="/?error=Username%20already%20exists", status_code=303)


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate(db, username, password)
    if not user:
        return RedirectResponse(url="/?error=Invalid%20credentials", status_code=303)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
