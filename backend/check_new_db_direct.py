import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def check_db_exists():
    db_url = os.getenv("DATABASE_URL")
    # Parse URL: mysql+pymysql://username:password@172.16.1.40:3306/opencats
    # We need to manually parse or use a library, but let's just do a direct pymysql test
    
    # Simple parsing for the sake of the test
    # url: mysql+pymysql://db_user:Paradigm%24%25678@172.16.1.40:3306/opencats
    user = "db_user"
    password = "Paradigm$%678"
    host = "172.16.1.40"
    port = 3306
    
    print(f"--- Attempting Direct Pymysql Connection to {host} ---")
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            connect_timeout=15
        )
        print("✅ Connection Successful!")
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            dbs = [row[0] for row in cursor.fetchall()]
            print(f"Available Databases: {dbs}")
            if 'paradigmitindia' in dbs:
                print("🏁 FOUND 'paradigmitindia'!")
            else:
                print("❌ 'paradigmitindia' NOT FOUND.")
        conn.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    check_db_exists()
