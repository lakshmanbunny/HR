import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Site Table ---")
        try:
            sites = conn.execute(text("SELECT * FROM site")).fetchall()
            for s in sites:
                print(s)
        except Exception as e:
            print(f"Error reading site table: {e}")

        print("\n--- Last 10 Candidates (Actual DB) ---")
        query = text("SELECT candidate_id, first_name, last_name, date_created, phone_cell FROM candidate ORDER BY date_created DESC LIMIT 10")
        res = conn.execute(query).fetchall()
        for row in res:
            print(row)

        print("\n--- Search for 'Anandha' in ATTACHMENT text (Resume) ---")
        # Sometimes names are only in resumes
        query_att = text("SELECT attachment_id, data_item_id, title FROM attachment WHERE LOWER(text) LIKE '%anandha%' OR text LIKE '%9393%'")
        res_att = conn.execute(query_att).fetchall()
        if res_att:
            print(f"✅ Found in attachment text!")
            for row in res_att:
                print(row)
        else:
            print(f"❌ Not found in attachment text")

if __name__ == "__main__":
    debug_data()
