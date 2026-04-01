import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def check_db_exists():
    # Use the existing URL but strip the DB name to check for others
    db_url = os.getenv("DATABASE_URL")
    # Base URL without the 'opencats' at the end
    base_url = db_url.rsplit('/', 1)[0]
    engine = create_engine(base_url)
    
    with engine.connect() as conn:
        print("--- Checking for 'paradigmitindia' Database ---")
        try:
            dbs = conn.execute(text("SHOW DATABASES")).fetchall()
            db_list = [d[0] for d in dbs]
            print(f"Available Databases: {db_list}")
            if 'paradigmitindia' in db_list:
                print("✅ Found 'paradigmitindia'!")
            else:
                print("❌ 'paradigmitindia' NOT FOUND in the list.")
        except Exception as e:
            print(f"Error listing databases: {e}")

if __name__ == "__main__":
    check_db_exists()
