import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Case-Insensitive Search for 'GANESH' in ANY name column ---")
        query = text("""
            SELECT candidate_id, first_name, last_name, middle_name, phone_cell 
            FROM candidate 
            WHERE 
                LOWER(first_name) LIKE '%ganesh%' OR 
                LOWER(last_name) LIKE '%ganesh%' OR
                LOWER(middle_name) LIKE '%ganesh%'
        """)
        res = conn.execute(query).fetchall()
        if res:
            print(f"✅ Found {len(res)} matches for 'Ganesh':")
            for row in res:
                print(row)
        else:
            print(f"❌ No matches found for 'Ganesh' in this database.")

if __name__ == "__main__":
    debug_data()
