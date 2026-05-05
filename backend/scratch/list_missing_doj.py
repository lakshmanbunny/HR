from app.db.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("--- CANDIDATES OFFERED BUT MISSING DOJ ---")
q = text("""
    SELECT 
        c.candidate_id, 
        c.first_name, 
        c.last_name, 
        cj.status,
        j.title as job_title
    FROM candidate c 
    JOIN candidate_joborder cj ON c.candidate_id = cj.candidate_id 
    JOIN joborder j ON cj.joborder_id = j.joborder_id
    LEFT JOIN extra_field ef ON c.candidate_id = ef.data_item_id AND ef.field_name = 'Date of Joining' 
    WHERE cj.status IN (600, 800, 900) 
    AND (ef.value IS NULL OR ef.value = '')
""")

res = db.execute(q).fetchall()
print(f"{'ID':<6} | {'Name':<20} | {'Status':<6} | {'Job Title'}")
print("-" * 60)
for r in res:
    name = f"{r.first_name} {r.last_name}"
    print(f"{r.candidate_id:<6} | {name:<20} | {r.status:<6} | {r.job_title}")

print(f"\nTotal: {len(res)} candidates missing DOJ.")
db.close()
