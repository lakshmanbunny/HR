
from sqlalchemy import text
from app.db.database import SessionLocal
import json

def explore():
    db = SessionLocal()
    try:
        # 1. Search for candidates
        print("--- Searching Candidates ---")
        cand_query = text("SELECT candidate_id, first_name, last_name FROM candidate WHERE last_name IN ('Vinay', 'Kolla') OR first_name IN ('Nethi', 'Venu Gopal')")
        candidates = db.execute(cand_query).fetchall()
        
        for cand in candidates:
            c_id = cand[0]
            name = f"{cand[1]} {cand[2]}"
            print(f"\nCandidate ID: {c_id}, Name: {name}")
            
            # 2. Check attachments
            print("  Attachments:")
            att_query = text("SELECT attachment_id, original_filename, title FROM attachment WHERE data_item_id = :id AND data_item_type = 100")
            atts = db.execute(att_query, {"id": c_id}).fetchall()
            for att in atts:
                print(f"    - ID: {att[0]}, File: {att[1]}, Title: {att[2]}")
            
            # 3. Check extra fields
            print("  Extra Fields:")
            # In some OpenCATS versions, extra fields are in extra_field table
            try:
                ef_query = text("SELECT field_name, value FROM extra_field WHERE data_item_id = :id")
                fields = db.execute(ef_query, {"id": c_id}).fetchall()
                for f in fields:
                    print(f"    - Field: {f[0]}, Value: {f[1]}")
            except Exception as e:
                print(f"    - Error checking extra_field table: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    explore()
