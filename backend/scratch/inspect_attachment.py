from app.db.database import engine
from sqlalchemy import text

def inspect_attachment_schema():
    with engine.connect() as conn:
        res = conn.execute(text('DESCRIBE attachment'))
        for r in res:
            print(r)

if __name__ == "__main__":
    inspect_attachment_schema()
