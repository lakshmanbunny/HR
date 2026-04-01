import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

def run_test():
    days = 30
    # Fixed queries with cj. prefix for ambiguous columns
    date_filter_cj_created = f"AND cj.date_created >= DATE_SUB(NOW(), INTERVAL {days} DAY)"
    date_filter_job = f"AND date_created >= DATE_SUB(NOW(), INTERVAL {days} DAY)"

    queries = {
        "Total Active Openings": f"SELECT COUNT(*) FROM joborder WHERE (status = 'Active' OR status = '100') {date_filter_job}",
        "Enrolled Candidates (FIXED)": f"""
            SELECT COUNT(DISTINCT cj.candidate_id) 
            FROM candidate_joborder cj 
            JOIN joborder j ON cj.joborder_id = j.joborder_id 
            WHERE (j.status = 'Active' OR j.status = '100')
            {date_filter_cj_created}
        """,
        "Category Performance (FIXED)": f"""
            SELECT j.title, COUNT(cj.candidate_id) as total, SUM(CASE WHEN cj.status >= 500 THEN 1 ELSE 0 END) as success 
            FROM joborder j 
            JOIN candidate_joborder cj ON j.joborder_id = cj.joborder_id 
            WHERE 1=1 {date_filter_cj_created} 
            GROUP BY j.title ORDER BY total DESC LIMIT 8
        """
    }

    with engine.connect() as conn:
        print(f"Testing FIXED queries with DAYS={days}")
        for name, sql in queries.items():
            print(f"\n--- {name} ---")
            try:
                res = conn.execute(text(sql))
                if "SELECT COUNT" in sql:
                    print(f"Result: {res.fetchone()[0]}")
                else:
                    rows = res.fetchall()
                    print(f"Result Rows: {len(rows)}")
                    for r in rows:
                        print(f"  {r}")
            except Exception as e:
                print(f"FAILED: {e}")

if __name__ == "__main__":
    run_test()
