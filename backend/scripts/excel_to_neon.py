import os
import sys
import pandas as pd
import re
from sqlalchemy import create_engine

# Ensure we can import from app
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.database import SQLALCHEMY_DATABASE_URL

def clean_table_name(name):
    """Cleans excel sheet names to be valid safe SQL table names"""
    # Convert to lowercase, replace spaces with underscores, remove non-alphanumeric
    clean_name = re.sub(r'\W+', '_', name.lower().strip())
    # Ensure it doesn't start with a number
    if clean_name and clean_name[0].isdigit():
        clean_name = f"t_{clean_name}"
    return clean_name

def ingest_excel_to_neon(excel_path: str):
    """
    Reads an Excel file and writes each sheet as a separate table in the Neon DB.
    """
    db_url = SQLALCHEMY_DATABASE_URL
    if db_url and db_url.startswith("postgres://"):
         db_url = db_url.replace("postgres://", "postgresql://", 1)
         
    engine = create_engine(db_url)
    
    print(f"Reading Excel file: {excel_path}")
    try:
        # Read all sheets into a dictionary of DataFrames
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        
        print(f"Found {len(sheet_names)} sheets: {sheet_names}")
        
        for sheet in sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet)
            
            # Clean column names
            df.columns = [clean_table_name(str(col)) for col in df.columns]
            
            table_name = clean_table_name(sheet)
            print(f"--> Writing sheet '{sheet}' to table '{table_name}' ({len(df)} rows)...")

            # Write to database (replace if exists)
            df.to_sql(table_name, db_url, if_exists='replace', index=False)


            
        print("\n✅ Successfully ingested all sheets into Neon PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = r"C:\Users\lakshman.yvs\Desktop\HR\Medidata Requirement Fullfillment Data 1.xlsx"
        
    ingest_excel_to_neon(path)
