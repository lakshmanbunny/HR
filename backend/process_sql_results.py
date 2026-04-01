import os
import time
import json
import google.generativeai as genai
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load local environment
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEON_URL = "postgresql://neondb_owner:npg_5TvfU4MYdyxC@ep-wild-art-amr6ah4r-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
PDF_DIR = "SQL_results"

# Initialize Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def process_pdf(file_path):
    """Sends PDF to Gemini 2.0 Flash and extracts structured test results."""
    print(f"\n--- [AI] Processing: {os.path.basename(file_path)} ---")
    
    try:
        # Upload file to Gemini File API
        print(f"Uploading {file_path} to Gemini...")
        sample_file = genai.upload_file(path=file_path, display_name=os.path.basename(file_path))
        
        # Wait for file to be processed by Gemini backend
        print("Waiting for Gemini to process file...")
        while sample_file.state.name == "PROCESSING":
            time.sleep(2)
            sample_file = genai.get_file(sample_file.name)
            
        if sample_file.state.name == "FAILED":
            raise Exception("Gemini failed to process the PDF file.")

        prompt = """
        You are a highly analytical Technical Recruiter and SQL Expert.
        Analyze the attached SQL written test PDF.
        The document contains exactly 10 questions.
        
        1. Identify the Candidate Name.
        2. Identify the Result ID or Candidate ID (look for labels like 'Result ID' or in the filename).
        3. For each of the 10 questions:
           - Provide the SQL Topic (e.g., SELECT statements, JOINS, GROUP BY, Subqueries, Constraints, Window Functions).
           - Identify if the candidate's answer is Correct or Incorrect. 
           - CRITICAL: Answers marked with a GREEN CHECK or GREEN COLOR are CORRECT.
           - CRITICAL: Answers marked with a RED CROSS or RED COLOR are INCORRECT.
        
        Return ONLY a JSON object with this exact structure:
        {
            "candidate_id": "...",
            "candidate_name": "...",
            "questions": [
                {"number": 1, "topic": "...", "is_correct": true/false},
                ...
            ],
            "summary": {
                "total_score_out_of_10": X,
                "weakest_topics": ["Topic A", "Topic B"]
            }
        }
        """
        
        print("Generating structured analysis...")
        response = model.generate_content([sample_file, prompt])
        
        # Cleanup file from Gemini storage immediately
        genai.delete_file(sample_file.name)
        
        # Extract JSON from response
        text_content = response.text
        if "```json" in text_content:
            text_content = text_content.split("```json")[1].split("```")[0].strip()
        
        parsed_data = json.loads(text_content)
        return parsed_data
        
    except Exception as e:
        print(f"ERROR processing PDF: {e}")
        return None

def save_to_neon(data, filename):
    """Inserts the parsed JSON into the Neon PostgreSQL database."""
    try:
        engine = create_engine(NEON_URL)
        with engine.connect() as conn:
            query = text("""
                INSERT INTO sql_test_results (candidate_id, candidate_name, test_json, summary_score, weakest_topics, pdf_filename)
                VALUES (:cid, :name, :json_data, :score, :weak_topics, :fname)
            """)
            
            # Extract score numerically
            score = float(data.get("summary", {}).get("total_score_out_of_10", 0))
            
            conn.execute(query, {
                "cid": data.get("candidate_id"),
                "name": data.get("candidate_name"),
                "json_data": json.dumps(data.get("questions")),
                "score": score,
                "weak_topics": data.get("summary", {}).get("weakest_topics", []),
                "fname": filename
            })
            conn.commit()
            print(f"SUCCESS: Result stored in Neon for {data.get('candidate_name')}.")
            return True
    except Exception as e:
        print(f"ERROR saving to Neon: {e}")
        return False

if __name__ == "__main__":
    files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    print(f"Found {len(files)} PDFs for processing.")
    
    for filename in files:
        full_path = os.path.join(PDF_DIR, filename)
        result = process_pdf(full_path)
        if result:
            print("\nExtracted Analysis Summary:")
            print(f"Candidate: {result.get('candidate_name')} | Score: {result.get('summary', {}).get('total_score_out_of_10')}/10")
            
            # Save to DB
            save_to_neon(result, filename)
        else:
            print(f"Failed to extract data for {filename}")
        
        # Slight delay to avoid rate limiting if any
        time.sleep(1)
    
    print("\n--- BATCH PROCESSING COMPLETE ---")
