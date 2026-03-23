import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def explore_schema():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            for table in ['candidate', 'joborder', 'company', 'contact']:
                print(f"\n--- Table: {table} ---")
                try:
                    # Get columns
                    result = conn.execute(text(f"DESCRIBE {table};"))
                    columns = result.fetchall()
                    for col in columns:
                        print(f" - {col[0]} ({col[1]})")
                    
                    # Get sample data
                    df = pd.read_sql_query(text(f"SELECT * FROM {table} LIMIT 3;"), conn)
                    print("Sample Data:")
                    print(df.to_string())
                except Exception as te:
                    print(f"Error exploring {table}: {str(te)}")
    except Exception as e:
        print(f"Connection Failed: {str(e)}")

if __name__ == "__main__":
    explore_schema()
