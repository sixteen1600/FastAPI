# pip install fastapi nest-asyncio pyngrok uvicorn pydantic pydantic[email] bcrypt firebase-admin python-dotenv
# uvicorn main:app --host 127.0.0.1 --port 8000 --reload


# Step 2: Importing Necessary Libraries and Classes
# ====================================================================================================================================================
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

from sqlalchemy import Date
from pydantic import EmailStr

# Step 3: Creating a FastAPI Instance and SetUp the Database
# ====================================================================================================================================================
DATABASE_URL = "sqlite:///./test2.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

# Step 4: Defining the Database Model
# ====================================================================================================================================================
# SQLAlchemy 的 Column 裡面只能放像 Integer、String、Date 這些資料庫型態。
class UserClassSQLAlchemy(Base):
    __tablename__ = "UsersTable"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String)
    birthday = Column(Date)
    userID = Column(String)
    usePassword = Column(String)


# Step 5: Creating Database Tables
# ====================================================================================================================================================
# Create tables
Base.metadata.create_all(bind=engine) # 它有個特性：只有當資料表不存在時才會建立，如果資料表已經存在，它不會去覆蓋、不會刪除、不會清空。

from datetime import date  # 要加這個 import
import bcrypt

session = SessionLocal()
try:
    dbisEmpty = session.query(UserClassSQLAlchemy).count()
    if (dbisEmpty == 0): # 確保只有在沒有資料時才新增，避免重複
        print("確認無資料，開始新增")
        use1 = UserClassSQLAlchemy(
            name = "Alice",
            age = 25,
            email = "alice0517@gmail.com",
            birthday = date(1999,5,17),
            userID = "Alice0517",
            usePassword = bcrypt.hashpw(",zi?<B])m8UaR09R".encode(), bcrypt.gensalt()).decode() ,
        )
        use2 = UserClassSQLAlchemy(
            name = "Bob",
            age = 30,
            email = "bob0823@gmail.com",
            birthday = date(1994,8,23),
            userID = "Bob0823",
            usePassword = bcrypt.hashpw("M{rUuV9-F/,>(@]G".encode(), bcrypt.gensalt()).decode() ,
        )
        session.add_all([use1, use2])
        session.commit()
    else:
        print("已有資料存於DataBase")
finally:
    session.close()

# Step 6: Dependency for Getting the Database Session
# ====================================================================================================================================================
# Dependency to get the database session
# 搭配 Depends 自動把 db 傳到 API 函式裡，並在 Step 8 使用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 7: Pydantic Model for Request Data and Response Data
# ====================================================================================================================================================
# create
from datetime import date
from typing import Annotated
from pydantic import Field
class UserCreate (BaseModel):
    name: Annotated[str, Field(min_length=1)]
    age: Annotated[int, Field(gt=0)]
    email: Annotated[EmailStr, Field()]
    birthday: Annotated[date, Field()] # SQLAlchemy 建表用自己的 Date；Pydantic 驗證資料用 Python datetime.date。兩邊要分清楚
    userID: Annotated[str, Field(min_length=1)]
    userPassword: Annotated[str, Field(min_length=8)]
    
# response 
"""
把回傳資料依照 ItemResponse 的結構整理
避免回傳多餘、錯誤或敏感的資料
參考Step 8
"""
class UserResponse(BaseModel):
    id:int
    name:str
    age:int
    email:EmailStr
    birthday:date


# ====================================================================


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI()

from fastapi import Depends
from auth import get_current_user

origins = ["*"]

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 static 資料夾供 CSS/JS 等使用
app.mount("/static", StaticFiles(directory="static"), name="static")

# 掛載 templates 資料夾供 HTML 使用
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/user", response_class=HTMLResponse)
def user_page(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

# @app.on_event("startup")
# def start_up():
    

# Step 8: API Endpoint to Create an Item
# ====================================================================================================================================================
"""
∵回傳的是 一群人（比如：查詢全部的使用者）
∴所以是「UserResponse 的清單」=> 也就是使用List
"""
# 查詢所有使用者
from typing import List 
@app.get("/allUsers", response_model=List[UserResponse]) # 回傳的是 一群人（比如：查詢全部的使用者）
async def get_allusers(db:Session = Depends(get_db)):
    db_all_users = db.query(UserClassSQLAlchemy).all() # 因為 .query() 要的是「模型類別」
    print(f"從資料庫撈到的資料：{db_all_users}")
    return db_all_users

# 查詢一個使用者
# ====================================================================================================================================================
@app.get("/oneUser/{user_id}", response_model=UserResponse) # 回傳的是 一群人（比如：查詢全部的使用者）
async def get_one_user(user_id:int, db:Session = Depends(get_db)):
    db_one_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if db_one_user is None:
        raise HTTPException(status_code=404, detail="無該使用者，請問要新增嗎")
    return db_one_user

# 建立一個使用者
# ====================================================================================================================================================
import bcrypt
@app.post("/createUser",response_model=UserResponse)
async def create_user(user:UserCreate, db: Session = Depends(get_db)):
    #db_user = UserClassSQLAlchemy(**user.model_dump()) # 相等於 User(username="Alice", email="alice@example.com", password="123456")
    hased_password = bcrypt.hashpw(user.userPassword.encode(), bcrypt.gensalt())
    db_user = UserClassSQLAlchemy(
        name = user.name,
        age = user.age,
        email = user.email,
        birthday = user.birthday,
        userID = user.userID,
        userPassword = hased_password.decode()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 修改一個使用者
# ====================================================================================================================================================
# 在此新增一個「可以局部修改」的模型
from typing import Optional
class UserUpdate(BaseModel):
    name:Optional[str] = None # None的意思 : 這個欄位可以不用填寫，如果不填，就預設是 None。
    age:Optional[int] = None
    email:Optional[EmailStr] = None
    birthday:Optional[date] = None
    

@app.put("/updateUser/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate,db:Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="查無此使用者，是否要先新增?")
    else:
        update_data = user_update.model_dump(exclude_unset=True) # # exclude_unset=True 只更新有給新值的欄位
        for key,value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        # db.refresh(物件) 是在 提交 commit() 之後，從資料庫重新抓一次該物件的最新資料回來，更新到 Python 記憶體中(的那個instance)
        db.refresh(db_user) # 可以協助我們抓最新的 id、其他資料
        return db_user

# 刪除一個使用者
# ====================================================================================================================================================
@app.delete("/deleteUser/{user_id}", response_model=UserResponse) # 回傳的是 一群人（比如：查詢全部的使用者）
async def delete_user(user_id:int, db:Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="無該使用者")
    else:
        db.delete(db_user)
        db.commit()
        # 刪除不需要refresh        
        raise HTTPException(status_code=200, detail="成功刪除")

# register API
# ====================================================================================================================================================
@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.userID == user.userID).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="使用者帳號已存在")
    
    hased_password = bcrypt.hashpw(user.userPassword.encode(), bcrypt.gensalt()).decode()

    db_user = UserClassSQLAlchemy(
        name = user.name,
        age = user.age,
        email = user.email,
        birthday = user.birthday,
        userID = user.userID,
        userPassword = hased_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# 建立 login API
# ====================================================================================================================================================
class UserLogin(BaseModel):
    userID: str
    userPassword: str

@app.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.userID == user.userID).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="查無此帳號")
    
    if not bcrypt.checkpw(user.userPassword.encode(), db_user.usePassword.encode()):
        raise HTTPException(status_code=401, detail="密碼錯誤")

    return {"message":f"{db_user.name}您好，登入成功，歡迎回來"}
    

# ====================================================================================================================================================




@app.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {"message":f"登入成功, 使用者代碼為 : {user['uid']}!"}

# ====================================================================================================================================================

from fastapi import Depends
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "")
admin_list = [email.strip() for email in ADMIN_EMAILS.split(",") if email.strip()]

@app.get("/whoami")
def who_am_i(user=Depends(get_current_user)):
    email = user.get("email", "")
    if email in admin_list:
        return {"role": "admin"}
    return {"role": "user"}

# ====================================================================================================================================================

from pydantic import BaseModel

class GoogleUser(BaseModel):
    name: str
    email: EmailStr
    uid: str

@app.post("/google_register")
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

class GoogleUser(BaseModel):
    name: str
    email: EmailStr
    uid: str

@app.post("/google_login_or_register")
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


from fastapi import Request

@app.get("/debug_token")
def debug_token(user=Depends(get_current_user), request: Request = None):
    """
    用來快速檢查 Firebase 傳入的 ID Token 是否能被成功驗證與解析。
    回傳 Firebase 提供的 token 中的資訊。
    """
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "firebase_claims": user,
        "request_headers": dict(request.headers)
    }
