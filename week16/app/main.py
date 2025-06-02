# pip install fastapi nest-asyncio pyngrok uvicorn sqlalchemy jinja2 pydantic pydantic[email] bcrypt firebase-admin python-dotenv
# uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import user_routes, admin_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(user_routes.router)
app.include_router(admin_routes.router)