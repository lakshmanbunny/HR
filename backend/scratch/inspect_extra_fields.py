from app.db.database import SessionLocal
from sqlalchemy import text
import json

def inspect():
    db = SessionLocal()
    try:
        # Check column names
        res = db.execute(text("DESCRIBE extra_field")).fetchall()
        print("--- extra_field Columns ---")
        for r in res:
            print(r)
            
        # Check sample data
        res = db.execute(text("SELECT * FROM extra_field LIMIT 10")).fetchall()
        print("\n--- extra_field Sample Data ---")
        for r in res:
            print(r)
            
        # Look for 'Joining' or 'DOJ' in field_name or similar
        # First find where field names are stored. In OpenCATS it's usually extra_field_settings
        res = db.execute(text("SHOW TABLES LIKE 'extra_field%'")).fetchall()
        print("\n--- Extra Field Tables ---")
        for r in res:
            print(r)
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect()
