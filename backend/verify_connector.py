import os
import sys

# Add backend dir to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "./"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.connectors import ProductionSqlConnector

def verify_schema_retrieval():
    print("--- Verifying ProductionSqlConnector Schema Retrieval ---")
    connector = ProductionSqlConnector()
    print(f"Detected Dialect: {connector.dialect}")
    
    schema = connector.get_schema()
    print("\nRETRIEVED SCHEMA PREVIEW:")
    print(schema[:1000] + "...")
    
    # Check if we specifically found candidate table
    if "Table: candidate" in schema:
        print("\n✅ SUCCESS: 'candidate' table successfully indexed in schema.")
    else:
        print("\n❌ FAILURE: 'candidate' table not found in schema.")

if __name__ == "__main__":
    verify_schema_retrieval()
