import os
import sys
import json

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

from app.chatbot.agent import ask_chatbot

def test_sourcing_flow():
    print(f"\n{'='*60}")
    print("PHASE 8: AI SOURCING ASSISTANT TEST (X-RAY SEARCH)")
    print(f"{'='*60}")

    history = []
    sourcing_context = {}

    # Turn 1: Initial request without location/exp
    question1 = "Can you help me source candidates for the .NET Medidata role?"
    print(f"\nUSER: {question1}")
    result1 = ask_chatbot(question1, history, sourcing_context)
    print(f"INTENT: {result1['intent']}")
    print(f"REPLY: {result1['reply']}")
    
    history.append({"role": "user", "content": question1})
    history.append({"role": "assistant", "content": result1["reply"]})
    sourcing_context = result1.get("sourcing_metadata", {})

    # Turn 2: Provide missing params
    question2 = "In Bangalore with 5+ years experience. I need around 5 candidates."
    print(f"\nUSER: {question2}")
    result2 = ask_chatbot(question2, history, sourcing_context)
    print(f"INTENT: {result2['intent']}")
    print(f"REPLY: {result2['reply']}")
    
    if result2.get("source_data"):
        try:
            candidates = json.loads(result2['source_data'])
            print(f"\nSUCCESS: SOURCED {len(candidates)} CANDIDATES")
            for i, c in enumerate(candidates[:5], 1):
                print(f"{i}. {c['title']}")
                print(f"   Link: {c['link']}")
        except Exception as e:
            print(f"Error parsing candidates: {e}")
            print(f"Raw data: {result2['source_data'][:200]}...")

if __name__ == "__main__":
    test_sourcing_flow()
