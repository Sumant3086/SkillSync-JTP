"""Application configuration management."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://skillsync_user:skillsync_password@database:5432/skillsync_db",
    )

    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "SkillSync"
    PROJECT_DESCRIPTION: str = "Explainable Collaborator Matching Platform"
    VERSION: str = "1.0.0"

    # Allow requests from the nginx-proxied frontend and direct dev access
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://frontend",
        "http://frontend:80",
    ]

    model_config = {"case_sensitive": True}


settings = Settings()
