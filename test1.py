# pip install fastapi nest-asyncio pyngrok uvicorn pydantic pydantic[email]
# uvicorn test1:app --host 127.0.0.1 --port 8000 --reload

# Step 2: Importing Necessary Libraries and Classes
# ====================================================================
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel


from sqlalchemy import Date
from pydantic import EmailStr

# Step 3: Creating a FastAPI Instance and SetUp the Database
DATABASE_URL = "sqlite:///./test2.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

# Step 4: Defining the Database Model
# SQLAlchemy 的 Column 裡面只能放像 Integer、String、Date 這些資料庫型態。
class UserClassSQLAlchemy(Base):
    __tablename__ = "UsersTable"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String)
    birthday = Column(Date)

# Step 5: Creating Database Tables
# Create tables
Base.metadata.create_all(bind=engine) # 它有個特性：只有當資料表不存在時才會建立，如果資料表已經存在，它不會去覆蓋、不會刪除、不會清空。

from datetime import date  # 要加這個 import
session = SessionLocal()
try:
    dbisEmpty = session.query(UserClassSQLAlchemy).count()
    if (dbisEmpty == 0): # 確保只有在沒有資料時才新增，避免重複
        print("確認無資料，開始新增")
        use1 = UserClassSQLAlchemy(
            name = "Alice",
            age = 25,
            email = "alice0517@gmail.com",
            birthday = date(1999,5,17)
        )
        use2 = UserClassSQLAlchemy(
            name = "Bob",
            age = 30,
            email = "bob0823@gmail.com",
            birthday = date(1994,8,23)
        )
        session.add_all([use1, use2])
        session.commit()
    else:
        print("已有資料存於DataBase")
finally:
    session.close()

# Step 6: Dependency for Getting the Database Session
# Dependency to get the database session
# 搭配 Depends 自動把 db 傳到 API 函式裡，並在 Step 8 使用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 7: Pydantic Model for Request Data and Response Data
# create
from datetime import date
class UserCreate (BaseModel): # BaseModel 才是 Pydantic 的資料驗證 model
    name:str
    age:int
    email:EmailStr
    birthday:date # SQLAlchemy 建表用自己的 Date；Pydantic 驗證資料用 Python datetime.date。兩邊要分清楚！

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
# from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse

app = FastAPI()
@app.get("/")
def root():
    return RedirectResponse(url="/docs")
    # return FileResponse("./index.html")

# @app.on_event("startup")
# def start_up():
    

# Step 8: API Endpoint to Create an Item
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
@app.get("/oneUser/{user_id}", response_model=UserResponse) # 回傳的是 一群人（比如：查詢全部的使用者）
async def get_one_user(user_id:int, db:Session = Depends(get_db)):
    db_one_user = db.query(UserClassSQLAlchemy).filter(UserClassSQLAlchemy.id == user_id).first()
    if db_one_user is None:
        raise HTTPException(status_code=404, detail="無該使用者，請問要新增嗎")
    return db_one_user

# 建立一個使用者
@app.post("/createUser",response_model=UserResponse)
async def create_user(user:UserCreate, db: Session = Depends(get_db)):
    db_user = UserClassSQLAlchemy(**user.model_dump()) # 相等於 User(username="Alice", email="alice@example.com", password="123456")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 修改一個使用者
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
        

# # ====================================================================
# fake_db_Keys = list(fake_db["users"].keys())
# # ====================================================================
# # 查詢所有使用者
# @app.get("/allUsers")
# def get_allUsers ():
#     return fake_db["users"]

# # 查詢一位使用者 
# @app.get("/user/{user_id}")
# def get_users(user_id:int):
#     if (user_id not in fake_db["users"]):
#         return {"error":"User not found"}
#     else:
#         return {"user":fake_db["users"][user_id]}

# # 新增一個使用者 
# @app.post("/user")
# def create_user(new_user_id:int, user:User):
#     #used_id = user_data.pop("id")
#     if (new_user_id not in fake_db_Keys):
#         new_user = jsonable_encoder(user)
#         fake_db["users"][new_user_id] = new_user
#         return new_user
#     else:
#         return "該使用者已存在，如果想要修改，請使用PUT功能"

# # 修改一位使用者
# from fastapi.encoders import jsonable_encoder
# @app.put("/user/{user_id}")
# def update_user(user_id:int, user:User):
#     if (user_id in fake_db_Keys):
#         update_user = jsonable_encoder(user)
#         fake_db["users"][user_id] = update_user
#         return update_user
#     else:
#         return "查無此使用者，請再次確認欲修改的使用者"

# # 刪除一位使用者
# from fastapi import HTTPException

# @app.delete("/user/{user_id}")
# def delete_user(user_id: int):    
#     if user_id in fake_db["users"]:
#         user = fake_db["users"].pop(user_id)
#         return {"user": user}
#     else:
#         raise HTTPException(status_code=404, detail="查無此使用者，請再次確認欲刪除的使用者")




# # ====================================================================
# print("測試")
# print("="*100)
# # 先檢查是否有這個ID，才能決定是否刪除

# fake_dbKeys = list(fake_db["users"].keys())
# print('fake_dbKKeys :',fake_dbKeys)
