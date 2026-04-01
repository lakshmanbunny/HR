import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

# Set GOOGLE_API_KEY environment variable if not already set
# os.environ["GOOGLE_API_KEY"] = "your_key_here" # It should be in .env

from app.chatbot.agent import ask_chatbot
from app.db.connectors import ProductionSqlConnector

def test_query(query, f):
    f.write(f"\n--- Testing Query: {query} ---\n")
    print(f"Testing: {query}")
    try:
        result = ask_chatbot(query)
        f.write(f"Generated SQL: {result.get('generated_sql')}\n")
        f.write(f"Reply: {result['reply']}\n")
        f.write(f"Source Data: {str(result['source_data'])}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")

if __name__ == "__main__":
    queries = [
        "today is 24th march 2026.can you tell me the recent hires", # Problematic query with markdown
        "can you tell me the details and status of Vijaya Sagar Talasila", # Conversational failure
        "can find candidate named anandha krishnan h",
        "which candidates are Placed?"
    ]
    
    with open("test_results_v2.txt", "w", encoding="utf-8") as f:
        for q in queries:
            test_query(q, f)
    print("Done. Results in test_results_v2.txt")
