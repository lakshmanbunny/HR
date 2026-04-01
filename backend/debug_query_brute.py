import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- All Sites ---")
        sites = conn.execute(text("SELECT site_id, name, unix_name FROM site")).fetchall()
        for s in sites:
            print(s)

        print("\n--- Last 5 Candidates ---")
        query = text("SELECT candidate_id, first_name, last_name, date_created FROM candidate ORDER BY date_created DESC LIMIT 5")
        res = conn.execute(query).fetchall()
        for row in res:
            print(row)

        print("\n--- Search for 'Anandha' in EVERYTHING (Brute Force) ---")
        # I'll search for 'Anandha' in every table that has a string column
        tables_query = text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'opencats' AND (data_type LIKE '%char%' OR data_type LIKE '%text%')")
        cols = conn.execute(tables_query).fetchall()
        
        found = False
        for table, col in cols:
            try:
                search_q = text(f"SELECT COUNT(*) FROM `{table}` WHERE `{col}` LIKE '%anandha%'")
                count = conn.execute(search_q).scalar()
                if count > 0:
                    print(f"✅ Found '{count}' occurrences in table '{table}', column '{col}'")
                    found = True
            except:
                continue
        
        if not found:
            print("❌ 'Anandha' not found in any string column in the entire 'opencats' database.")

if __name__ == "__main__":
    debug_data()
