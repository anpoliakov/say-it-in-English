from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db import engine, Base
from routers import words, users, translate
import storage
from settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Ensure MinIO bucket exists
    storage.ensure_bucket()
    yield

app = FastAPI(
    title="Say it in English API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # в проде сузить до домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(words.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(translate.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "dev_mode": settings.dev_mode}
