import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Searching for ANY phone number starting with or containing '756' ---")
        query_phone = text("""
            SELECT candidate_id, last_name, first_name, phone_cell, phone_home, phone_work 
            FROM candidate 
            WHERE 
                phone_cell LIKE '%756%' OR 
                phone_home LIKE '%756%' OR 
                phone_work LIKE '%756%'
        """)
        res_phone = conn.execute(query_phone).fetchall()
        if res_phone:
            print(f"✅ Found {len(res_phone)} matches for '756':")
            for row in res_phone:
                print(row)
        else:
            print(f"❌ No phone numbers found in the entire 'candidate' table containing '756'.")

if __name__ == "__main__":
    debug_data()
