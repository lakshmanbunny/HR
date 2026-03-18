import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Add the backend directory to sys.path to import models
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.db.database import engine as pg_engine

load_dotenv()

def fix_sequences():
    print("Resetting PostgreSQL sequences...")
    
    tables = [
        "candidates",
        "woxsen_candidates",
        "job_descriptions",
        "screening_results",
        "rag_metrics",
        "rag_retrieval_metrics",
        "rag_evaluation_results",
        "rag_evaluation_jobs",
        "rag_llm_metrics",
        "rag_llm_eval_jobs",
        "interview_sessions",
    ]
    
    Session = sessionmaker(bind=pg_engine)
    session = Session()
    
    try:
        for table_name in tables:
            print(f"Resetting sequence for {table_name}...")
            # Use text() for SQLAlchemy 2.0+ compatibility
            query = f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name}"
            session.execute(text(query))
        
        session.commit()
        print("Sequences reset successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error resetting sequences: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_sequences()
