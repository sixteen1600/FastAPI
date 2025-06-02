from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.models import UserClassSQLAlchemy
from app.database import get_db
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Annotated
from datetime import date
import bcrypt
from app.auth import get_current_user, is_admin_user

router = APIRouter()

class UserCreate(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    age: Annotated[int, Field(gt=0)]
    email: Annotated[EmailStr, Field()]
    birthday: Annotated[date, Field()]
    userID: Annotated[str, Field(min_length=1)]
    userPassword: Annotated[str, Field(min_length=8)]

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    birthday: date

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None

class UserLogin(BaseModel):
    userID: str
    userPassword: str

@router.get("/allUsers", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="只有管理者可以讀取使用者列表")
    return db.query(UserClassSQLAlchemy).all()

@router.post("/google_login_or_register")
def google_login_or_register(google_user: UserCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.email == google_user.email).first()
    if db_user:
        return {"message": "使用者已登入", "user_id": db_user.id}
    new_user = UserClassSQLAlchemy(
        name=google_user.name,
        age=0,
        email=google_user.email,
        birthday=date.today(),
        userID=google_user.userID,
        usePassword="GOOGLE_LOGIN"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "已完成註冊", "user_id": new_user.id}

@router.get("/whoami")
def who_am_i(user=Depends(get_current_user)):
    role = "admin" if is_admin_user(user) else "user"
    return {"role": role}