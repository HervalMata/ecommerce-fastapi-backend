from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.exceptions import ApiException, api_exception_handler
from app.db.database import engine
from app.core.config import settings
from sqlmodel import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Attempting to connect to the database...")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    print("Successfully connected to the database.")
    print("Successfully connected: {settings.DATABASE_URL}")
    yield

app = FastAPI(title="Ecommerce FastAPI Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

app.add_exception_handler(ApiException, api_exception_handler)

@app.get("/hello")
async def say_hello():
    return {"message": "Welcome to the Ecommerce FastAPI Backend!"}