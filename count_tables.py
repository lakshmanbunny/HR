import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.db.connectors import ProductionSqlConnector

def count_tables():
    db = ProductionSqlConnector()
    try:
        # We'll fetch the tables from information_schema
        # Using double quotes for the query string to handle quotes correctly
        query = "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'paradigmitindia'"
        result = db.execute_query(query)
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_tables()
