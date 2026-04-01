from app.db.database import engine, Base
from app.db import models

def init_db():
    print("Creating all tables defined in models...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
