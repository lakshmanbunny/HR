
import pymysql

host = "172.16.1.40"
user = "db_user"
password = "Paradigm$678"
db_name = "paradigmitindia"

try:
    connection = pymysql.connect(host=host, user=user, password=password, database=db_name, cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        print("Searching for Nethi Vinay and Venu Gopal Kolla...")
        cursor.execute("SELECT candidate_id, first_name, last_name FROM candidate WHERE first_name LIKE '%Nethi%' OR last_name LIKE '%Vinay%' OR first_name LIKE '%Venu%' OR last_name LIKE '%Kolla%'")
        candidates = cursor.fetchall()
        for cand in candidates:
            print(f"ID: {cand['candidate_id']}, Name: {cand['first_name']} {cand['last_name']}")
            
            # Check attachments
            print(f"  Attachments for {cand['candidate_id']}:")
            cursor.execute("SELECT attachment_id, original_filename, title FROM attachment WHERE data_item_id = %s AND data_item_type = 100", (cand['candidate_id'],))
            atts = cursor.fetchall()
            for att in atts:
                print(f"    - ID: {att['attachment_id']}, File: {att['original_filename']}, Title: {att['title']}")
            
            # Check extra fields (for test scores)
            print(f"  Extra Fields for {cand['candidate_id']}:")
            # In OpenCATS, extra fields are often in extra_field table or candidate table
            cursor.execute("SHOW TABLES LIKE 'extra_field'")
            if cursor.fetchone():
                cursor.execute("SELECT * FROM extra_field WHERE data_item_id = %s", (cand['candidate_id'],))
                fields = cursor.fetchall()
                for f in fields:
                    print(f"    - Field: {f.get('field_name')}, Value: {f.get('value')}")
            else:
                print("    - No extra_field table found.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
