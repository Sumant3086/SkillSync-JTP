"""SkillSync FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import SessionLocal, wait_for_db
from app.database.init_db import init_database, seed_data
from app.api.endpoints import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    print("Starting SkillSync backend...")
    wait_for_db()
    init_database()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    print("SkillSync backend ready!")
    yield
    # Shutdown: nothing to release


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.include_router(router, prefix=settings.API_V1_PREFIX)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint — service identity."""
    return {
        "name": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "status": "running",
    }
