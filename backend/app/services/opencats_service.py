from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import engine
from core.llm_service import LLMService
from config.logging_config import get_logger
import json
import httpx
import hashlib
import io
from pypdf import PdfReader

logger = get_logger(__name__)

class OpenCATSService:
    def __init__(self):
        self.llm_service = LLMService()

    def list_candidates(self, db: Session, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Fetches candidates directly from OpenCATS 'candidate' table.
        """
        query = text("""
            SELECT 
                candidate_id, first_name, last_name, email1, key_skills, date_created 
            FROM candidate 
            ORDER BY date_created DESC 
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).fetchall()
        
        candidates = []
        for row in result:
            candidates.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "name": f"{row[1]} {row[2]}",
                "email": row[3],
                "skills": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            })
        return candidates

    def get_candidate_resume_text(self, db: Session, candidate_id: int) -> Optional[str]:
        """
        Retrieves extracted resume text from OpenCATS 'attachment' table.
        """
        query = text("""
            SELECT text 
            FROM attachment 
            WHERE data_item_id = :candidate_id 
            AND data_item_type = 100 
            AND resume = 1 
            ORDER BY date_created DESC 
            LIMIT 1
        """)
        result = db.execute(query, {"candidate_id": candidate_id}).fetchone()
        return result[0] if result else None

    async def analyze_candidate(self, db: Session, candidate_id: int) -> Dict[str, Any]:
        """
        Analyzes candidate resume using Gemini 2.0 Flash with automatic PDF download fallback.
        """
        # 1. Fetch Candidate & Attachment Info
        query = text("""
            SELECT c.first_name, c.last_name, c.key_skills, 
                   a.attachment_id, a.text, a.directory_name, a.stored_filename
            FROM candidate c
            LEFT JOIN attachment a ON c.candidate_id = a.data_item_id AND a.resume = 1
            WHERE c.candidate_id = :id
            ORDER BY a.date_created DESC
            LIMIT 1
        """)
        row = db.execute(query, {"id": candidate_id}).fetchone()
        if not row:
            raise Exception("Candidate not found")

        first_name, last_name, key_skills, attachment_id, resume_text, directory_name, stored_filename = row

        # 2. Handle Missing Text with Auto-Download Fallback
        if not resume_text:
            if attachment_id and directory_name:
                logger.info(f"Text missing for candidate {candidate_id}. Attempting auto-download from OpenCATS...")
                try:
                    # Construct OpenCATS direct download URL
                    directory_hash = hashlib.md5(directory_name.encode()).hexdigest()
                    base_url = "http://172.16.1.40/paradigmitindia" # Should probably be in settings
                    download_url = f"{base_url}/index.php?m=attachments&a=getAttachment&id={attachment_id}&directoryNameHash={directory_hash}"
                    
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(download_url, timeout=15.0)
                        if resp.status_code == 200:
                            # Extract text from the downloaded PDF
                            reader = PdfReader(io.BytesIO(resp.content))
                            resume_text = ""
                            for page in reader.pages:
                                resume_text += page.extract_text() + "\n"
                            logger.info(f"Successfully extracted {len(resume_text)} chars from auto-downloaded PDF.")
                except Exception as e:
                    logger.error(f"Auto-download failed for candidate {candidate_id}: {e}")

        if not resume_text:
            return {
                "error": "No resume text found and auto-download failed. OpenCATS extraction was empty.",
                "candidate_name": f"{first_name} {last_name}"
            }

        # 3. Prompt Gemini for Analysis
        from datetime import datetime
        current_date = datetime.now().strftime("%d %B %Y")
        
        prompt = f"""
        You are an elite AI Recruiter. Today's date is {current_date}. 
        Analyze the following resume for a candidate.
        
        CANDIDATE: {first_name} {last_name}
        KEY SKILLS (from DB): {key_skills}
        
        RESUME TEXT:
        {resume_text}
        
        Provide a deep-dive analysis in the following JSON format:
        {{
            "risk_analysis": ["bullet points of potential risks, gaps, or concerns"],
            "strengths": ["bullet points of key technical and soft strengths"],
            "initial_call_questions": ["5 precise questions the HR should ask in the first screening call to verify their background"]
        }}
        
        Return ONLY the JSON.
        """
        
        logger.info(f"Analyzing candidate {candidate_id} with Gemini 2.0 Flash")
        response = self.llm_service.llm.invoke(prompt)
        content = response.content
        
        # Clean JSON response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            analysis = json.loads(content)
            analysis["candidate_name"] = f"{first_name} {last_name}"
            return analysis
        except Exception as e:
            logger.error(f"Failed to parse AI analysis for candidate {candidate_id}: {e}")
            return {
                "error": "Failed to generate AI analysis",
                "raw_content": content
            }

    async def analyze_candidate_file(self, db: Session, candidate_id: int, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyzes an uploaded PDF/Docx directly for a candidate.
        """
        # 1. Fetch Candidate Info
        cand_query = text("SELECT first_name, last_name, key_skills FROM candidate WHERE candidate_id = :id")
        cand = db.execute(cand_query, {"id": candidate_id}).fetchone()
        
        # 2. Extract Text from PDF
        text_content = ""
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {filename}: {e}")
            return {"error": f"Failed to extract text from PDF: {str(e)}"}

        if not text_content.strip():
            return {"error": "Extracted text is empty. Please ensure the PDF is not an image-only scan."}

        # 3. Prompt Gemini
        from datetime import datetime
        current_date = datetime.now().strftime("%d %B %Y")
        
        prompt = f"""
        You are an elite AI Recruiter. Today's date is {current_date}.
        Analyze the following resume for a candidate.
        
        CANDIDATE: {cand[0] if cand else 'Unknown'} {cand[1] if cand else ''}
        
        RESUME CONTENT (EXTRACTED FROM UPLOADED PDF):
        {text_content}
        
        Provide a deep-dive analysis in the following JSON format:
        {{
            "risk_analysis": ["bullet points of potential risks, gaps, or concerns"],
            "strengths": ["bullet points of key technical and soft strengths"],
            "initial_call_questions": ["5 precise questions the HR should ask in the first screening call"]
        }}
        
        Return ONLY the JSON.
        """
        
        logger.info(f"Analyzing uploaded resume for candidate {candidate_id} with Gemini 2.0 Flash")
        response = self.llm_service.llm.invoke(prompt)
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            analysis = json.loads(content)
            analysis["candidate_name"] = f"{cand[0]} {cand[1]}" if cand else "Unknown"
            return analysis
        except Exception as e:
            return {"error": "Failed to parse AI analysis", "raw_content": content}

opencats_service = OpenCATSService()
