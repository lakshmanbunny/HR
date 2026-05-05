from app.db.database import engine
from sqlalchemy import text

def list_tables():
    with engine.connect() as conn:
        res = conn.execute(text('SHOW TABLES'))
        tables = [r[0] for r in res]
        for t in tables:
            print(t)

if __name__ == "__main__":
    list_tables()
