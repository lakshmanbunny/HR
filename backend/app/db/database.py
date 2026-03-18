import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get Database URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Fallback to SQLite for local development if DATABASE_URL is not set
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(BACKEND_DIR, "paradigm_ai.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Create engine
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15}
    )
    # Enable WAL for SQLite if needed (though we're migrating away)
else:
    # For PostgreSQL (Neon)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
