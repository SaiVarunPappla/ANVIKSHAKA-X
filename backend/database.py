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

logger = logging.getLogger(__name__)

# Database URL — SQLite for dev; PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./anvikshaka.db")

# Normalize Supabase/Vercel Postgres URL format
# Supabase provides postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info("[DATABASE] Normalized postgres:// to postgresql:// for SQLAlchemy")

logger.info(f"[DATABASE] Using database: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL[:50]}")

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
