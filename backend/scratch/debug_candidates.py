from app.db.database import engine
from sqlalchemy import text

def check_candidate_data():
    with engine.connect() as conn:
        res = conn.execute(text('SELECT COUNT(*) FROM candidate'))
        count = res.scalar()
        print(f"Total candidates in 'candidate' table: {count}")
        
        if count > 0:
            res = conn.execute(text('SELECT candidate_id, first_name, last_name, site_id FROM candidate LIMIT 5'))
            for r in res:
                print(r)

if __name__ == "__main__":
    check_candidate_data()
