"""

database.py

-----------

SQLAlchemy engine, session factory, and Base declarative model.

Uses SQLite for development (PostgreSQL is the production target).

"""



from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, declarative_base

import os



# -------------------------------------------------------------------

# Database URL — SQLite for dev; in production swap to PostgreSQL:

#   postgresql+psycopg2://user:pass@host:5432/anvikshaka

# -------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./anvikshaka.db")



# check_same_thread=False is required for SQLite + FastAPI threading

engine = create_engine(

   DATABASE_URL,

   connect_args={"check_same_thread": False},

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