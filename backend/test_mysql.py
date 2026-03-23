import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    db_url = os.getenv("DATABASE_URL")
    print(f"Connecting to: {db_url.split('@')[-1]}") # Print only host part for safety
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # MySQL query to list tables
            result = conn.execute(text("SHOW TABLES;"))
            tables = result.fetchall()
            print(f"Connection Successful! Found {len(tables)} tables.")
            print("Tables found:")
            for t in tables[:10]:
                print(f" - {t[0]}")
    except Exception as e:
        print(f"Connection Failed: {str(e)}")

if __name__ == "__main__":
    test_connection()
