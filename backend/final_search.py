import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Final Case-Insensitive Search for 'ANANDHA' (Entire DB String Columns) ---")
        tables_query = text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'opencats' AND (data_type LIKE '%char%' OR data_type LIKE '%text%')")
        cols = conn.execute(tables_query).fetchall()
        
        found_name = False
        for table, col in cols:
            try:
                search_q = text(f"SELECT COUNT(*) FROM `{table}` WHERE LOWER(`{col}`) LIKE '%anandha%'")
                count = conn.execute(search_q).scalar()
                if count > 0:
                    print(f"✅ Found '{count}' occurrences in table '{table}', column '{col}'")
                    found_name = True
            except:
                continue
        
        if not found_name:
            print("❌ 'Anandha' (case-insensitive) not found anywhere in the entire database.")

        print("\n--- Final Case-Insensitive Search for '9393' (Entire DB String Columns) ---")
        found_phone = False
        for table, col in cols:
            try:
                search_q = text(f"SELECT COUNT(*) FROM `{table}` WHERE `{col}` LIKE '%9393%'")
                count = conn.execute(search_q).scalar()
                if count > 0:
                    print(f"✅ Found '{count}' occurrences in table '{table}', column '{col}'")
                    found_phone = True
            except:
                continue
        
        if not found_phone:
            print("❌ Phone suffix '9393' not found anywhere in the entire database.")

if __name__ == "__main__":
    debug_data()
