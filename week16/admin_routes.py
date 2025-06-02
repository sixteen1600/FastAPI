from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user, is_admin_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, user=Depends(get_current_user)):
    if not is_admin_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你沒有權限進入此頁面")
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})

@router.get("/user", response_class=HTMLResponse)
def user_page(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})