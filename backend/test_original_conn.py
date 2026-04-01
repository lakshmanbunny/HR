import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def test_opencats():
    user = "db_user"
    password = "Paradigm$%678"
    host = "172.16.1.40"
    db = "opencats"
    
    print(f"--- Attempting Connection to {host} ({db}) ---")
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            connect_timeout=15
        )
        print("✅ Connection Successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_opencats()
