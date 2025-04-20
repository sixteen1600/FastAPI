# pip install fastapi nest-asyncio pyngrok uvicorn pydantic
# uvicorn test1:app --host 127.0.0.1 --port 8000 --reload

# Schema 
# ====================================================================
from datetime import date
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str
    birthday: date

# fake db 一個假的資料庫，方便我們進行新增、修改、刪除與查詢
# ====================================================================
fake_db = {
    "users": {
        1: {
            "name": "Kai",
            "age": 25,
            "email": "Kai@fakemail.com",
            "birthday": "2000-01-01",
        },
        2: {
            "name": "Jane",
            "age": 27,
            "email": "jane@fakemail.com",
            "birthday": "1998-12-04",
        }
    }
}

# ====================================================================
# from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse

app = FastAPI()
@app.get("/")
def root():
    # return RedirectResponse(url="/docs")
    return FileResponse("./index.html")

# ====================================================================
fake_db_Keys = list(fake_db["users"].keys())

# 查詢所有使用者
@app.get("/allUsers")
def get_allUsers ():
    return fake_db["users"]

# 查詢一位使用者 
@app.get("/user/{user_id}")
def get_users(user_id:int):
    if (user_id not in fake_db["users"]):
        return {"error":"User not found"}
    else:
        return {"user":fake_db["users"][user_id]}

# 新增一個使用者 
@app.post("/user")
def create_user(new_user_id:int, user:User):
    #used_id = user_data.pop("id")
    if (new_user_id not in fake_db_Keys):
        new_user = jsonable_encoder(user)
        fake_db["users"][new_user_id] = new_user
        return new_user
    else:
        return "該使用者已存在，如果想要修改，請使用PUT功能"

# 修改一位使用者
from fastapi.encoders import jsonable_encoder
@app.put("/user/{user_id}")
def update_user(user_id:int, user:User):
    if (user_id in fake_db_Keys):
        update_user = jsonable_encoder(user)
        fake_db["users"][user_id] = update_user
        return update_user
    else:
        return "查無此使用者，請再次確認欲修改的使用者"

# 刪除一位使用者
@app.delete("/user/{user_id}")
def delete_user(user_id:int):    
    if (user_id in fake_db_Keys):
        user = fake_db["users"].pop(user_id)
        return user
    else:
        return "查無此使用者，請再次確認欲刪除的使用者"


# ====================================================================
print("測試")
print("="*100)
# 先檢查是否有這個ID，才能決定是否刪除

fake_dbKeys = list(fake_db["users"].keys())
print('fake_dbKKeys :',fake_dbKeys)