from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, get_db
from app.models import *  # noqa: F401, F403 — register models for create_all
from app.routers import evidence, ingredients, processing, search, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (SQLite dev mode)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="DontEatCancer API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredients.router, prefix="/api/v1")
app.include_router(evidence.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(processing.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/stats")
def stats(db=Depends(get_db)):
    from app.services import evidence_service, ingredient_service

    ing_stats = ingredient_service.get_stats(db)
    ev_stats = evidence_service.get_stats(db)
    return {**ing_stats, **ev_stats}
