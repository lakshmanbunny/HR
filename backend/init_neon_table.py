import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

NEON_URL = "postgresql://neondb_owner:npg_5TvfU4MYdyxC@ep-wild-art-amr6ah4r-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"

def init_db():
    try:
        engine = create_engine(NEON_URL)
        with engine.connect() as conn:
            # Drop if exists for clean start during this POC phase
            # conn.execute(text("DROP TABLE IF EXISTS sql_test_results;"))
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS sql_test_results (
                id SERIAL PRIMARY KEY,
                candidate_id VARCHAR(50),
                candidate_name VARCHAR(255),
                test_json JSONB,
                summary_score FLOAT,
                weakest_topics TEXT[],
                pdf_filename VARCHAR(255),
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            conn.execute(text(create_table_query))
            conn.commit()
            print("SUCCESS: sql_test_results table created in Neon.")
    except Exception as e:
        print(f"FAILED to init Neon table: {e}")

if __name__ == "__main__":
    init_db()
