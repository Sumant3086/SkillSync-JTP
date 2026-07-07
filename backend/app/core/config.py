"""Application configuration management."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://skillsync_user:skillsync_password@database:5432/skillsync_db"
    )
    
    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "SkillSync"
    PROJECT_DESCRIPTION: str = "Explainable Collaborator Matching Platform"
    VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://frontend:5173"]
    
    class Config:
        case_sensitive = True


settings = Settings()
