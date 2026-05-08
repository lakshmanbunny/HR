
from sqlalchemy import text
from app.db.database import SessionLocal

def find_vinay():
    db = SessionLocal()
    try:
        print("--- Searching for Nethi Vinay ---")
        q = text("SELECT candidate_id, first_name, last_name FROM candidate WHERE first_name LIKE :n OR last_name LIKE :n")
        res = db.execute(q, {"n": "%Nethi%"}).fetchall()
        for r in res:
            print(f"ID: {r[0]}, Name: {r[1]} {r[2]}")
            
            # Attachments
            print("  Attachments:")
            aq = text("SELECT attachment_id, original_filename FROM attachment WHERE data_item_id = :id AND data_item_type = 100")
            atts = db.execute(aq, {"id": r[0]}).fetchall()
            for a in atts:
                print(f"    - ID: {a[0]}, File: {a[1]}")
            
            # Extra fields
            print("  Extra Fields:")
            eq = text("SELECT field_name, value FROM extra_field WHERE data_item_id = :id")
            fields = db.execute(eq, {"id": r[0]}).fetchall()
            for f in fields:
                print(f"    - {f[0]}: {f[1]}")
    finally:
        db.close()

if __name__ == "__main__":
    find_vinay()
