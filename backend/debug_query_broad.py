import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Global Stats ---")
        count_query = text("SELECT COUNT(*) FROM candidate")
        total = conn.execute(count_query).scalar()
        print(f"Total Candidates: {total}")
        
        sites_query = text("SELECT DISTINCT site_id FROM candidate")
        sites = conn.execute(sites_query).fetchall()
        print(f"Distinct Site IDs: {[s[0] for s in sites]}")

        print("\n--- Exhaustive Phone Search (Digits Only) ---")
        # In MySQL, we can use REGEXP or REPLACE to ignore dashes
        # But let's just search for the sequence of numbers
        query = text("SELECT candidate_id, last_name, first_name, phone_cell, site_id FROM candidate WHERE REPLACE(REPLACE(REPLACE(phone_cell, '-', ''), ' ', ''), '–', '') LIKE '%8790019393%'")
        res = conn.execute(query).fetchall()
        if res:
            print(f"✅ Found matches for phone:")
            for row in res:
                print(row)
        else:
            print(f"❌ No matches found for phone '8790019393'")

        print("\n--- Case-Insensitive Name Search ---")
        query_name = text("SELECT candidate_id, last_name, first_name, site_id FROM candidate WHERE LOWER(first_name) LIKE '%anandha%' OR LOWER(last_name) LIKE '%anandha%'")
        res_name = conn.execute(query_name).fetchall()
        if res_name:
            print(f"✅ Found matches for 'Anandha':")
            for row in res_name:
                print(row)
        else:
            print(f"❌ No matches found for 'Anandha'")

if __name__ == "__main__":
    debug_data()
