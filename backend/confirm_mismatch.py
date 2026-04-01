import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def debug_data():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("--- Searching for User's Candidates ---")
        candidates_to_find = [
            ("Sai Ganesh", "Bajjuri", "986-607-3844"),
            ("Ganesh", "Nallamothu", "990-196-4427"),
            ("Ganesh", "Sale", "756-909-9087"),
            ("Ganesh", "Cheekati", "834-147-5747")
        ]
        
        for first, last, cell in candidates_to_find:
            query = text("SELECT candidate_id, first_name, last_name, phone_cell FROM candidate WHERE (first_name LIKE :first AND last_name LIKE :last) OR phone_cell LIKE :cell")
            res = conn.execute(query, {"first": f"%{first}%", "last": f"%{last}%", "cell": f"%{cell}%"}).fetchall()
            if res:
                print(f"✅ FOUND match for {first} {last}:")
                for row in res:
                    print(row)
            else:
                print(f"❌ NOT FOUND: {first} {last} ({cell})")

        print("\n--- Search for 'JAI GANESH' (Which I found earlier) ---")
        query_jai = text("SELECT candidate_id, first_name, last_name, phone_cell FROM candidate WHERE first_name LIKE '%JAI%' AND first_name LIKE '%GANESH%'")
        res_jai = conn.execute(query_jai).fetchall()
        if res_jai:
            print(f"✅ Found 'JAI GANESH' in THIS database:")
            for row in res_jai:
                print(row)
        else:
            print(f"❌ 'JAI GANESH' not found (Wait, I found it earlier? Checking again...)")

if __name__ == "__main__":
    debug_data()
