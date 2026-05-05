from app.db.database import engine
from sqlalchemy import text

def check_resume_text():
    with engine.connect() as conn:
        res = conn.execute(text('SELECT attachment_id, data_item_id, text FROM attachment WHERE resume = 1 AND text IS NOT NULL AND text != "" LIMIT 5'))
        rows = res.fetchall()
        print(f"Found {len(rows)} resumes with text extraction.")
        for r in rows:
            print(f"Attachment ID: {r[0]}, Candidate ID: {r[1]}, Text Snippet: {r[2][:100]}...")

if __name__ == "__main__":
    check_resume_text()
