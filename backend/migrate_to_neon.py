import os
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, select, insert
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Add the backend directory to sys.path to import models
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.db.database import Base, engine as pg_engine
from app.db.models import Candidate, WoxsenCandidate, JobDescription, ScreeningResult, RAGMetric, RAGRetrievalMetric, RAGEvaluationResult, RAGEvaluationJob, RAGLLMMetric, RAGLLMEvalJob, InterviewSession

load_dotenv()

SQLITE_DB_PATH = os.path.join(backend_dir, "paradigm_ai.db")
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    print("Error: DATABASE_URL not found in .env")
    sys.exit(1)

def migrate():
    print(f"Starting migration from SQLite ({SQLITE_DB_PATH}) to Neon PostgreSQL...")
    
    # Create tables in PostgreSQL
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Order of migration (independent tables first)
    tables = [
        ("candidates", Candidate),
        ("woxsen_candidates", WoxsenCandidate),
        ("job_descriptions", JobDescription),
        ("screening_results", ScreeningResult),
        ("rag_metrics", RAGMetric),
        ("rag_retrieval_metrics", RAGRetrievalMetric),
        ("rag_evaluation_results", RAGEvaluationResult),
        ("rag_evaluation_jobs", RAGEvaluationJob),
        ("rag_llm_metrics", RAGLLMMetric),
        ("rag_llm_eval_jobs", RAGLLMEvalJob),
        ("interview_sessions", InterviewSession),
    ]
    
    Session = sessionmaker(bind=pg_engine)
    session = Session()
    
    try:
        for table_name, model in tables:
            print(f"Migrating table: {table_name}...")
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  No data in {table_name}, skipping.")
                continue
            
            # Convert sqlite rows to list of dicts
            data = [dict(row) for row in rows]
            
            # Bulk insert into PostgreSQL
            # We use the model's table object directly for insertion
            session.execute(insert(model.__table__), data)
            print(f"  Migrated {len(data)} rows.")
        
        session.commit()
        print("Migration completed successfully!")
        
        # Reset sequences for PostgreSQL (important for auto-increment IDs)
        print("Resetting sequences...")
        for table_name, _ in tables:
            session.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name}")
        session.commit()
        print("Sequences reset.")

    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
    finally:
        session.close()
        sqlite_conn.close()

if __name__ == "__main__":
    migrate()
