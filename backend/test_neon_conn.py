import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Use the Neon URL from the .env check
NEON_URL = "postgresql://neondb_owner:npg_5TvfU4MYdyxC@ep-wild-art-amr6ah4r-pooler.c-5.us-east-1.aws.neon.tech/neondb"

def test_neon():
    try:
        print(f"Connecting to Neon...")
        # Add sslmode=require if needed, though often default for Neon
        url = NEON_URL + "?sslmode=require"
        engine = create_engine(url)
        with engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).fetchone()
            print(f"SUCCESS! Connected to Neon. Version: {res[0]}")
            return True
    except Exception as e:
        print(f"FAILED to connect to Neon: {e}")
        return False

if __name__ == "__main__":
    test_neon()
