# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. Setup Database URL (Uses a local file for SQLite)
# We will create 'user_auth.db' in the project root
SQLALCHEMY_DATABASE_URL = "sqlite:///./user_auth.db"

# 2. Create the SQLAlchemy Engine
# The connect_args is needed for SQLite to handle multi-threading/async operations
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a Session Local class
# Each database transaction will use an instance of this class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Base class for models
# This will be the base class for any database model you define.
Base = declarative_base()

# 5. Dependency for Database Session (Used in FastAPI Endpoints)
# This is a generator that yields a database session and ensures it closes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()