from app.db.database import engine
from sqlalchemy import text

def debug_attachment():
    with engine.connect() as conn:
        # Find candidate ID for Lakshman YVS
        res = conn.execute(text("SELECT candidate_id FROM candidate WHERE first_name LIKE 'Lakshman%' AND last_name LIKE 'YVS%'"))
        cand = res.fetchone()
        if not cand:
            print("Candidate Lakshman YVS not found.")
            return
        
        cand_id = cand[0]
        print(f"Candidate ID: {cand_id}")
        
        # Check attachments
        res = conn.execute(text("SELECT attachment_id, title, original_filename, resume, data_item_type, text FROM attachment WHERE data_item_id = :id"), {"id": cand_id})
        attachments = res.fetchall()
        print(f"Found {len(attachments)} attachments for candidate {cand_id}:")
        for a in attachments:
            print(f"ID: {a[0]}, Title: {a[1]}, Filename: {a[2]}, Resume: {a[3]}, Type: {a[4]}, HasText: {bool(a[5])}")

if __name__ == "__main__":
    debug_attachment()
