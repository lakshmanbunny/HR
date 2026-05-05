from app.db.database import engine
from sqlalchemy import text

def debug_attachment_path():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT attachment_id, stored_filename, directory_name FROM attachment WHERE data_item_id = 279"))
        for r in res:
            print(f"ID: {r[0]}, Stored: {r[1]}, Dir: {r[2]}")

if __name__ == "__main__":
    debug_attachment_path()
