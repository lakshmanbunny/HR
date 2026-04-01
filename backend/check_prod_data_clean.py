import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def check_prod_db():
    user = "db_user"
    password = "Paradigm$%678"
    host = "172.16.1.40"
    db = "paradigmitindia"
    
    print(f"--- Attempting Connection to {host} ({db}) ---")
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            connect_timeout=15,
            charset='utf8mb4'
        )
        print("SUCCESS: Connection Successful!")
        with conn.cursor() as cursor:
            print("\n--- Searching for 'Anandha' in Production DB ---")
            cursor.execute("SELECT candidate_id, first_name, last_name, phone_cell FROM candidate WHERE LOWER(first_name) LIKE '%anandha%' OR LOWER(last_name) LIKE '%anandha%'")
            res = cursor.fetchall()
            if res:
                print(f"MATCH FOUND: Anandha Krishnan!")
                for row in res:
                    print(row)
            else:
                print("FAIL: 'Anandha' still not found in this database.")
                
            print("\n--- Searching for 'Ganesh Sale' ---")
            # Searching for cell 756-909-9087
            cursor.execute("SELECT candidate_id, first_name, last_name, phone_cell FROM candidate WHERE phone_cell LIKE '%756%909%9087%'")
            res_ganesh = cursor.fetchall()
            if res_ganesh:
                print(f"MATCH FOUND: Ganesh Sale!")
                for row in res_ganesh:
                    print(row)
            else:
                print("FAIL: 'Ganesh Sale' still not found.")
                
            print("\n--- Overall Stats ---")
            cursor.execute("SELECT COUNT(*) FROM candidate")
            total = cursor.fetchone()[0]
            print(f"Total Candidates in this DB: {total}")
            
        conn.close()
    except Exception as e:
        print(f"ERROR: Connection Failed: {e}")

if __name__ == "__main__":
    check_prod_db()
