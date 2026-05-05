from app.db.database import engine
from sqlalchemy import text

def find_working_candidate():
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT c.candidate_id, c.first_name, c.last_name 
            FROM candidate c 
            JOIN attachment a ON c.candidate_id = a.data_item_id 
            WHERE a.resume = 1 AND a.text IS NOT NULL AND a.text != '' 
            LIMIT 5
        """))
        for r in res:
            print(f"Working Candidate: {r[0]} - {r[1]} {r[2]}")

if __name__ == "__main__":
    find_working_candidate()
