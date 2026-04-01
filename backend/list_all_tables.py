import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

def list_tables():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found!")
        return

    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"--- Tables in Database ({len(tables)} total) ---")
        for table in sorted(tables):
            print(f"- {table}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
