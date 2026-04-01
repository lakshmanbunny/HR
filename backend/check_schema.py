import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

tables_to_check = ['joborder', 'candidate', 'candidate_joborder', 'company', 'activity']
expected_cols = {
    'joborder': ['joborder_id', 'status', 'date_created', 'recruiter', 'title'],
    'candidate': ['candidate_id', 'date_created', 'source'],
    'candidate_joborder': ['candidate_id', 'joborder_id', 'status', 'date_created', 'date_modified'],
    'activity': ['activity_id', 'date_created', 'joborder_id', 'data_item_id', 'notes']
}

with engine.connect() as conn:
    print("--- Database Schema Check ---")
    for table in tables_to_check:
        try:
            res = conn.execute(text(f"DESCRIBE {table}")).fetchall()
            actual_cols = [r[0] for r in res]
            print(f"\nTable: {table}")
            print(f"  Existing Columns: {', '.join(actual_cols)}")
            
            if table in expected_cols:
                missing = [c for c in expected_cols[table] if c not in actual_cols]
                if missing:
                    print(f"  *** MISSING COLUMNS: {missing} ***")
                else:
                    print(f"  All expected columns present.")
        except Exception as e:
            print(f"\nTable: {table} - ERROR: {e}")
