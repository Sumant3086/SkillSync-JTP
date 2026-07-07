"""SkillSync FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import SessionLocal, wait_for_db
from app.database.init_db import init_database, seed_data
from app.api.endpoints import router


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Include API routes
app.include_router(router, prefix=settings.API_V1_PREFIX)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    print("Starting SkillSync backend...")
    
    # Wait for database to be ready
    wait_for_db()
    
    # Initialize database schema
    init_database()
    
    # Seed data (idempotent)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    
    print("✓ SkillSync backend ready!")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SkillSync Backend",
        "database": "connected"
    }
