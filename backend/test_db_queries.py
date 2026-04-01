import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import datetime

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    print("--- DB Connections Test ---")
    now_res = conn.execute(text("SELECT NOW(), VERSION()")).fetchone()
    print(f"DB Current Time (NOW()): {now_res[0]}")
    print(f"DB Version: {now_res[1]}")
    
    print("\n--- Job Order Status ---")
    res = conn.execute(text("SELECT status, COUNT(*) FROM joborder GROUP BY status")).fetchall()
    for row in res:
        print(f"Status '{row[0]}': {row[1]}")
        
    print("\n--- Active Jobs Check ---")
    # Exact query from repository.py (simplified)
    query_raw = "SELECT COUNT(*) FROM joborder WHERE (status = 'Active' OR status = '100')"
    res = conn.execute(text(query_raw)).fetchone()
    print(f"Total Active (No Date Filter): {res[0]}")
    
    query_date = "SELECT COUNT(*) FROM joborder WHERE (status = 'Active' OR status = '100') AND date_created >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    res = conn.execute(text(query_date)).fetchone()
    print(f"Total Active (Last 30 Days Filter): {res[0]}")
    
    print("\n--- Candidate Job Order Check ---")
    query_cj = "SELECT COUNT(*) FROM candidate_joborder"
    res = conn.execute(text(query_cj)).fetchone()
    print(f"Total Candidate Job Orders: {res[0]}")
    
    query_cj_date = "SELECT COUNT(*) FROM candidate_joborder WHERE date_created >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    res = conn.execute(text(query_cj_date)).fetchone()
    print(f"Total Enrolled (Last 30 Days Filter): {res[0]}")

    print("\n--- Sample Date Created Values (JobOrder) ---")
    res = conn.execute(text("SELECT date_created FROM joborder WHERE status = 'Active' LIMIT 5")).fetchall()
    for row in res:
        print(f"Job created_at: {row[0]} (Type: {type(row[0])})")
