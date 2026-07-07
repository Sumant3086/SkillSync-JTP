"""Database session management with connection retry logic."""
import time
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_retries: int = 30, retry_interval: int = 2):
    """
    Wait for database to be ready with connection retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_interval: Seconds to wait between retries
    
    Raises:
        Exception: If database connection fails after max_retries
    """
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✓ Database connection established successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            else:
                raise Exception(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
