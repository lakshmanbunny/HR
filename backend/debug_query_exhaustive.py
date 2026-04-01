import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Checking for Other Databases ---")
        try:
            dbs = conn.execute(text("SHOW DATABASES")).fetchall()
            print(f"Databases: {[d[0] for d in dbs]}")
        except Exception as e:
            print(f"Error listing databases: {e}")

        print("\n--- Exhaustive Search for Phone '9393' in ANY column ---")
        query_phone = text("""
            SELECT candidate_id, last_name, first_name, phone_cell, phone_home, phone_work 
            FROM candidate 
            WHERE 
                phone_cell LIKE '%9393%' OR 
                phone_home LIKE '%9393%' OR 
                phone_work LIKE '%9393%'
        """)
        res_phone = conn.execute(query_phone).fetchall()
        if res_phone:
            print(f"✅ Found matches for '9393':")
            for row in res_phone:
                print(row)
        else:
            print(f"❌ No matches found for '9393' in any phone column")

        print("\n--- Exhaustive Search for 'Anandha' in ANY column ---")
        # Search in first_name, last_name, middle_name, notes, key_skills
        query_text = text("""
            SELECT candidate_id, last_name, first_name 
            FROM candidate 
            WHERE 
                LOWER(first_name) LIKE '%anandha%' OR 
                LOWER(last_name) LIKE '%anandha%' OR
                LOWER(middle_name) LIKE '%anandha%' OR
                LOWER(notes) LIKE '%anandha%' OR
                LOWER(key_skills) LIKE '%anandha%'
        """)
        res_text = conn.execute(query_text).fetchall()
        if res_text:
            print(f"✅ Found matches for 'Anandha':")
            for row in res_text:
                print(row)
        else:
            print(f"❌ No matches found for 'Anandha' in any text column")

        print("\n--- Checking Inactive Candidates ---")
        query_inactive = text("SELECT COUNT(*) FROM candidate WHERE is_active = 0")
        inactive_count = conn.execute(query_inactive).scalar()
        print(f"Inactive Candidates: {inactive_count}")

if __name__ == "__main__":
    debug_data()
