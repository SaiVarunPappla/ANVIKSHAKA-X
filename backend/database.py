"""
database.py
-----------
SQLAlchemy engine, session factory, and Base declarative model.
Uses SQLite for development (PostgreSQL is the production target).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL — SQLite for dev; PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./anvikshaka.db")

# Configure engine based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # check_same_thread=False is required for SQLite + FastAPI threading
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
