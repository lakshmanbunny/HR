from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_jd_table():
    engine = create_engine(DATABASE_URL)
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        jd_text TEXT,
        jd_hash VARCHAR(255) UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        INDEX (jd_hash),
        INDEX (created_at)
    );
    """
    
    with engine.connect() as conn:
        print("Executing CREATE TABLE for job_descriptions...")
        conn.execute(text(create_table_sql))
        conn.commit()
        print("Successfully created/verified job_descriptions table.")

if __name__ == "__main__":
    create_jd_table()
