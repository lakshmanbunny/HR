import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        search_val = "8790019393"
        search_name = "anandha"
        
        print(f"--- Searching Contact Table for '{search_name}' and '{search_val}' ---")
        query_contact = text("""
            SELECT contact_id, last_name, first_name, phone_work, phone_cell 
            FROM contact 
            WHERE 
                LOWER(first_name) LIKE '%anandha%' OR 
                LOWER(last_name) LIKE '%anandha%' OR
                phone_work LIKE '%9393%' OR
                phone_cell LIKE '%9393%'
        """)
        res_contact = conn.execute(query_contact).fetchall()
        if res_contact:
            print(f"✅ Found matches in contact:")
            for row in res_contact:
                print(row)
        else:
            print(f"❌ No matches in contact")

        print(f"\n--- Searching User Table for '{search_name}' ---")
        query_user = text("""
            SELECT user_id, last_name, first_name, email 
            FROM user 
            WHERE LOWER(first_name) LIKE '%anandha%' OR LOWER(last_name) LIKE '%anandha%'
        """)
        res_user = conn.execute(query_user).fetchall()
        if res_user:
            print(f"✅ Found matches in user:")
            for row in res_user:
                print(row)
        else:
            print(f"❌ No matches in user")

        print(f"\n--- Searching Activity Notes for '{search_name}' or '{search_val}' ---")
        query_act = text("""
            SELECT activity_id, notes 
            FROM activity 
            WHERE LOWER(notes) LIKE '%anandha%' OR notes LIKE '%9393%'
            LIMIT 5
        """)
        res_act = conn.execute(query_act).fetchall()
        if res_act:
            print(f"✅ Found matches in activity:")
            for row in res_act:
                print(row)
        else:
            print(f"❌ No matches in activity")

        print("\n--- Listing ALL Table Column counts to see where data might hide ---")
        tables_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'opencats'")
        tables = conn.execute(tables_query).fetchall()
        for (t,) in tables:
            c = conn.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
            if c > 0:
                print(f"Table '{t}': {c} rows")

if __name__ == "__main__":
    debug_data()
