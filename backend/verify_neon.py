import os
from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Add the backend directory to sys.path to import models
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.db.database import engine as pg_engine
from app.db.models import Candidate, WoxsenCandidate, JobDescription, ScreeningResult, RAGMetric, RAGRetrievalMetric, RAGEvaluationResult, RAGEvaluationJob, RAGLLMMetric, RAGLLMEvalJob, InterviewSession

load_dotenv()

def verify():
    print("Verifying data in Neon PostgreSQL...")
    
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
            count = session.query(func.count(model.id)).scalar()
            print(f"Table {table_name}: {count} rows")
            
        print("Verification completed.")

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify()
