
import pymysql

host = "172.16.1.40"
user = "db_user"
password = "Paradigm$%678"
db_name = "paradigmitindia"

try:
    connection = pymysql.connect(host=host, user=user, password=password, database=db_name, cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        print("Checking text field for attachment 675...")
        sql = "SELECT text FROM attachment WHERE attachment_id = 675"
        cursor.execute(sql)
        res = cursor.fetchone()
        if res and res['text']:
            print(f"Text found (length: {len(res['text'])})")
            print(res['text'][:500])
        else:
            print("No text found in DB field.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
