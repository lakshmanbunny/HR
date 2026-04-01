import os
import sys
import pandas as pd
import io

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.db.connectors import ProductionSqlConnector

def export_overview():
    db = ProductionSqlConnector()
    
    # Tables to include
    tables = [
        'candidate', 'joborder', 'company', 'candidate_joborder', 
        'candidate_joborder_status', 'activity', 'contact',
        'extra_field', 'candidate_source'
    ]
    
    output_path = "db_overview.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Database Overview & Sample Data\n\n")
        f.write("Generated on: 2026-03-24\n\n")
        
        for table in tables:
            print(f"Exporting {table}...")
            f.write(f"## Table: `{table}`\n\n")
            
            # Get Schema
            schema_query = f"DESCRIBE `{table}`"
            try:
                result = db.execute_query(schema_query)
                if isinstance(result, str) and not result.startswith("Error"):
                    # Convert CSV string back to DataFrame for markdown formatting
                    df = pd.read_csv(io.StringIO(result))
                    f.write("### Schema\n\n")
                    f.write(df.to_markdown(index=False))
                    f.write("\n\n")
                else:
                    f.write(f"Schema Query Result: {result}\n\n")
            except Exception as e:
                f.write(f"Schema exception for {table}: {e}\n\n")
            
            # Get Sample Data (Top 10)
            sample_query = f"SELECT * FROM `{table}` LIMIT 10"
            try:
                result = db.execute_query(sample_query)
                if isinstance(result, str) and not result.startswith("Error") and "returned 0 results" not in result:
                    df = pd.read_csv(io.StringIO(result))
                    f.write("### Sample Data (Top 10 rows)\n\n")
                    # Truncate long strings for readability
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            df[col] = df[col].apply(lambda x: (str(x)[:50] + '...') if len(str(x)) > 50 else x)
                    
                    f.write(df.to_markdown(index=False))
                    f.write("\n\n")
                else:
                    f.write(f"Sample Query Result: {result}\n\n")
            except Exception as e:
                f.write(f"Sample exception for {table}: {e}\n\n")
                
            f.write("---\n\n")

    print(f"Done! Overview saved to {output_path}")

if __name__ == "__main__":
    export_overview()
