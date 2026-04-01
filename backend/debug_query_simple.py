import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Direct Query for Phone: 8790019393 ---")
        # Search for digits only
        query = text("SELECT candidate_id, last_name, first_name, phone_cell FROM candidate WHERE phone_cell LIKE '%879%001%9393%'")
        res = conn.execute(query).fetchall()
        if res:
            print(f"✅ Found matches:")
            for row in res:
                print(row)
        else:
            print(f"❌ No matches found for pattern '%879%001%9393%'")

        print("\n--- Direct Query for Name: Anandha ---")
        query_name = text("SELECT candidate_id, last_name, first_name FROM candidate WHERE first_name LIKE '%Anandha%' OR last_name LIKE '%Anandha%'")
        res_name = conn.execute(query_name).fetchall()
        if res_name:
            print(f"✅ Found matches for 'Anandha':")
            for row in res_name:
                print(row)
        else:
            print(f"❌ No matches found for 'Anandha'")
            
        print("\n--- Data Sample (First 20 Candidates) ---")
        sample_query = text("SELECT first_name, last_name, phone_cell FROM candidate LIMIT 20")
        sample_res = conn.execute(sample_query).fetchall()
        for row in sample_res:
            print(row)

if __name__ == "__main__":
    debug_data()
