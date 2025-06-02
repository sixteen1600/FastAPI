from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/user", response_class=HTMLResponse)
def user_page(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

import os
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()  # 確保可以讀取 .env

@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


