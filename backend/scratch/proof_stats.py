from app.db.database import SessionLocal
from sqlalchemy import text
from datetime import datetime

db = SessionLocal()

print("--- PROOF 1: OFFERS VS DOJ ---")
q1 = text("""
    SELECT cj.candidate_id, cj.status, ef.value as doj 
    FROM candidate_joborder cj 
    LEFT JOIN extra_field ef ON cj.candidate_id = ef.data_item_id AND ef.field_name = 'Date of Joining' 
    WHERE cj.status IN (600, 800, 900) 
    AND cj.date_created >= DATE_SUB(NOW(), INTERVAL 30 DAY)
""")
res1 = db.execute(q1).fetchall()
print(f"Total Offers Released (Last 30 Days): {len(res1)}")
for r in res1:
    print(f"Candidate: {r.candidate_id} | Status: {r.status} | DOJ: {r.doj}")

print("\n--- PROOF 2: ENROLLED VS SUBMISSIONS ---")
# Enrolled (Unique Candidates)
q2 = text("""
    SELECT COUNT(DISTINCT candidate_id) 
    FROM candidate_joborder 
    WHERE date_created >= DATE_SUB(NOW(), INTERVAL 30 DAY)
""")
enrolled = db.execute(q2).scalar()
print(f"Enrolled (Unique Candidates): {enrolled}")

# Submissions (Total Job Assignments)
q3 = text("""
    SELECT COUNT(*) 
    FROM candidate_joborder 
    WHERE status >= 100 
    AND date_created >= DATE_SUB(NOW(), INTERVAL 30 DAY)
""")
submissions = db.execute(q3).scalar()
print(f"Submissions (Total Assignments): {submissions}")

# Check for duplicates (One candidate in multiple jobs)
q4 = text("""
    SELECT candidate_id, COUNT(*) as jobs 
    FROM candidate_joborder 
    WHERE date_created >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    GROUP BY candidate_id 
    HAVING jobs > 1
""")
dupes = db.execute(q4).fetchall()
print(f"Candidates assigned to multiple jobs: {len(dupes)}")
for d in dupes:
    print(f"Candidate {d.candidate_id} is in {d.jobs} jobs")

db.close()
