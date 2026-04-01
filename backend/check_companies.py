import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Companies in current DB ---")
        query = text("SELECT company_id, name FROM company LIMIT 10")
        res = conn.execute(query).fetchall()
        for row in res:
            print(row)

if __name__ == "__main__":
    debug_data()
