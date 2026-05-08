import pymysql
conn = pymysql.connect(host='172.16.1.40', user='db_user', password='Paradigm$678', database='paradigmitindia')
cur = conn.cursor()
cur.execute('DESCRIBE candidate')
print("=== candidate columns ===")
for row in cur.fetchall():
    print(row[0], '-', row[1])
conn.close()
