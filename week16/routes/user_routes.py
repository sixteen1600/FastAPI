from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import UserClassSQLAlchemy
from app.database import get_db
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Annotated
from datetime import date
import bcrypt
from app.auth import get_current_user
import os
from dotenv import load_dotenv


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

from dotenv import load_dotenv
load_dotenv()

import os

@router.get("/allUsers", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db), user=Depends(get_current_user)):
    admin_env = os.getenv("ADMIN_EMAILS")
    print("🔍 .env 中的 ADMIN_EMAILS =", admin_env)

    admin_list = [email.strip() for email in admin_env.split(",") if email.strip()]
    print("👤 登入者 email:", user.get("email"))
    print("🛡️ admin 列表:", admin_list)

    if user.get("email") not in admin_list:
        raise HTTPException(status_code=403, detail="只有管理者可以讀取使用者列表")

    return db.query(UserClassSQLAlchemy).all()



@router.get("/oneUser/{user_id}", response_model=UserResponse)
async def get_one_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="無該使用者")
    return user

@router.post("/createUser", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.userPassword.encode(), bcrypt.gensalt()).decode()
    db_user = UserClassSQLAlchemy(
        name=user.name,
        age=user.age,
        email=user.email,
        birthday=user.birthday,
        userID=user.userID,
        usePassword=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/updateUser/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="查無此使用者")
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/deleteUser/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="無該使用者")
    db.delete(db_user)
    db.commit()
    return db_user

@router.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.userID == user.userID).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="查無此帳號")
    if not bcrypt.checkpw(user.userPassword.encode(), db_user.usePassword.encode()):
        raise HTTPException(status_code=401, detail="密碼錯誤")
    return {"message": f"{db_user.name}您好，登入成功，歡迎回來"}

load_dotenv()
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "")
admin_list = [email.strip() for email in ADMIN_EMAILS.split(",") if email.strip()]

# 判斷身份
@router.get("/whoami")
def who_am_i(user=Depends(get_current_user)):
    email = user.get("email", "")
    if email in admin_list:
        return {"role": "admin"}
    return {"role": "user"}

# Google 註冊
class GoogleUser(BaseModel):
    name: str
    email: EmailStr
    uid: str

@router.post("/google_register")
def google_register(google_user: GoogleUser, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.email == google_user.email).first()
    
    if db_user:
        return {"message": "使用者已存在", "user_id": db_user.id}

    new_user = UserClassSQLAlchemy(
        name=google_user.name,
        age=0,
        email=google_user.email,
        birthday=date.today(),
        userID=google_user.uid,
        usePassword="GOOGLE_LOGIN"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "已註冊新使用者", "user_id": new_user.id}

# Google 登入/註冊
@router.post("/google_login_or_register")
def google_login_or_register(google_user: GoogleUser, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.email == google_user.email).first()

    if db_user:
        return {"message": "使用者已登入", "user_id": db_user.id}

    new_user = UserClassSQLAlchemy(
        name=google_user.name,
        age=0,
        email=google_user.email,
        birthday=date.today(),
        userID=google_user.uid,
        usePassword="GOOGLE_LOGIN"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "已完成註冊", "user_id": new_user.id}

# Token 偵錯
@router.get("/debug_token")
def debug_token(user=Depends(get_current_user), request: Request = None):
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "firebase_claims": user,
        "request_headers": dict(request.headers)
    }