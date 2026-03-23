from .database import engine, Base
from . import models

def init_db():
    print("--- [DB] Initializing Database Schema... ---")
    try:
        Base.metadata.create_all(bind=engine)
        print("--- [DB] Database Schema Synchronized. ---")
    except Exception as e:
        print(f"--- [DATABASE] Skipped schema creation (likely Read-Only): {str(e)} ---")
