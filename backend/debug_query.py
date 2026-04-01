import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Checking Phone Number Format ---")
        # Try different formats for the phone number
        phone_formats = ['879-001-9393', '8790019393', '(879) 001-9393', '879.001.9393']
        
        for fmt in phone_formats:
            query = text("SELECT candidate_id, last_name, first_name, phone_cell, phone_home, phone_work FROM candidate WHERE phone_cell = :fmt OR phone_home = :fmt OR phone_work = :fmt")
            res = pd.read_sql_query(query, conn, params={"fmt": fmt})
            if not res.empty:
                print(f"✅ Found with format '{fmt}':")
                print(res)
            else:
                print(f"❌ Not found with format '{fmt}'")

        print("\n--- Searching for 'Anandha' (Partial Match) ---")
        query_name = text("SELECT candidate_id, last_name, first_name FROM candidate WHERE first_name LIKE :name OR last_name LIKE :name")
        res_name = pd.read_sql_query(query_name, conn, params={"name": "%Anandha%"})
        if not res_name.empty:
            print(f"✅ Found matches for 'Anandha':")
            print(res_name)
        else:
            print(f"❌ No matches found for 'Anandha'")
            
        print("\n--- Showing Sample Phone Numbers to see actual format ---")
        sample_query = text("SELECT phone_cell, phone_home, phone_work FROM candidate WHERE phone_cell != '' AND phone_cell IS NOT NULL LIMIT 5")
        sample_res = pd.read_sql_query(sample_query, conn)
        print(sample_res)

if __name__ == "__main__":
    debug_data()
