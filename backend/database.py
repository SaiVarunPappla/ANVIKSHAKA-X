"""
database.py
-----------
SQLAlchemy engine, session factory, and Base declarative model.
Uses SQLite for development (PostgreSQL is the production target).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging
import re

logger = logging.getLogger(__name__)


def get_database_url():
    """
    Select and sanitize database URL from environment variables.
    Priority: DATABASE_URL > POSTGRES_URL_NON_POOLING > POSTGRES_URL > sqlite default
    """
    # Try environment variables in priority order
    for env_var in ["DATABASE_URL", "POSTGRES_URL_NON_POOLING", "POSTGRES_URL"]:
        raw_value = os.getenv(env_var, "").strip()
        
        if not raw_value:
            continue
            
        # Remove surrounding quotes if present
        raw_value = raw_value.strip('"').strip("'")
        
        # Remove accidental "ENV_VAR_NAME=" prefix if present
        # e.g., "DATABASE_URL=postgres://..." -> "postgres://..."
        if "=" in raw_value and raw_value.split("=")[0].isupper():
            raw_value = raw_value.split("=", 1)[1].strip()
        
        # Check if this looks like a valid database URL
        if raw_value.startswith(("postgres://", "postgresql://", "sqlite://")):
            logger.info(f"[DATABASE] Selected URL from: {env_var}")
            
            # Normalize postgres:// to postgresql:// for SQLAlchemy
            if raw_value.startswith("postgres://"):
                raw_value = raw_value.replace("postgres://", "postgresql://", 1)
                logger.info("[DATABASE] Normalized postgres:// to postgresql:// for SQLAlchemy")
            
            # Log scheme and masked connection info
            scheme = raw_value.split("://")[0]
            has_query_params = "?" in raw_value
            
            # Mask the host for security
            if "@" in raw_value:
                masked = raw_value.split("@")[0] + "@***"
            else:
                masked = raw_value[:30] + "..."
                
            logger.info(f"[DATABASE] Scheme: {scheme}, Has query params: {has_query_params}")
            logger.info(f"[DATABASE] Connection: {masked}")
            
            return raw_value
    
    # Fallback to SQLite for local development
    logger.info("[DATABASE] No PostgreSQL URL found, using SQLite default")
    return "sqlite:///./anvikshaka.db"


# Get and normalize database URL
DATABASE_URL = get_database_url()

# Configure engine based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # check_same_thread=False is required for SQLite + FastAPI threading
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        echo=False,
        pool_pre_ping=True,  # Verify connections before using them
    )
    logger.info("[DATABASE] Engine created successfully")
except Exception as e:
    logger.error(f"[DATABASE] Failed to create engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
