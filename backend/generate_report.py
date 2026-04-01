import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def generate_full_schema_report():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    db_name = engine.url.database
    
    report_file = "opencats_schema_overview.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# OpenCats Database Schema Overview\n\n")
        f.write(f"**Database:** {db_name}\n")
        f.write(f"**Generated at:** 2026-03-23\n\n")
        
        try:
            with engine.connect() as conn:
                # Get all tables
                tables_result = conn.execute(text("SHOW TABLES;"))
                tables = [t[0] for t in tables_result.fetchall()]
                
                f.write(f"Total Tables found: {len(tables)}\n\n")
                f.write("## Table List\n")
                for t in tables:
                    f.write(f"- [{t}](#table-{t.replace('_', '-')})\n")
                f.write("\n---\n\n")
                
                for table in tables:
                    print(f"Processing table: {table}...")
                    f.write(f"### Table: {table}\n\n")
                    
                    # Get column definitions
                    try:
                        cols_result = conn.execute(text(f"DESCRIBE `{table}`;"))
                        cols = cols_result.fetchall()
                        f.write("| Column | Type | Null | Key | Default | Extra |\n")
                        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
                        for col in cols:
                            f.write(f"| {col[0]} | {col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]} |\n")
                        f.write("\n")
                    except Exception as e:
                        f.write(f"*Error fetching columns: {str(e)}*\n\n")
                    
                    # Get sample data (first 3 rows)
                    try:
                        df = pd.read_sql_query(text(f"SELECT * FROM `{table}` LIMIT 3;"), conn)
                        if df.empty:
                            f.write("*No data available in this table.*\n\n")
                        else:
                            f.write("**Sample Data (First 3 rows):**\n\n")
                            f.write(df.to_markdown(index=False))
                            f.write("\n\n")
                    except Exception as e:
                        f.write(f"*Error fetching sample data: {str(e)}*\n\n")
                    
                    f.write("---\n\n")
                    
            print(f"Done! Report generated at {report_file}")
            
        except Exception as e:
            f.write(f"# Error Connecting to Database\n{str(e)}")
            print(f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    generate_full_schema_report()
