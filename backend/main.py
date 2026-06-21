from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storage import get_storage
from words.router import router as words_router
from users.router import router as users_router
from game.router import router as game_router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage bucket is ready on startup
    get_storage().ensure_bucket()
    yield


app = FastAPI(
    title="Say it in English API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в проде сузить до домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(words_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(game_router, prefix="/api")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "dev_mode": settings.dev_mode}
