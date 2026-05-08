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
import docx
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
        You are an elite Technical Recruiter. Today's date is {current_date}. 
        Analyze the following resume for a candidate.
        
        CANDIDATE: {first_name} {last_name}
        KEY SKILLS (from DB): {key_skills}
        
        RESUME TEXT:
        {resume_text}
        
        Provide a deep-dive analysis in the following JSON format:
        {{
            "risk_analysis": ["bullet points of potential risks, gaps, or concerns"],
            "strengths": ["bullet points of key technical and soft strengths"],
            "initial_call_questions": [
                {{
                    "question": "The question text",
                    "expected_answer": "A 'Cheat Sheet' for HR. Give 2-3 specific keywords or technical terms the candidate MUST mention. Add one simple 'Check' question the HR can ask to verify. DO NOT use generic phrases like 'should demonstrate understanding'."
                }}
            ]
        }}
        
        IMPORTANT RULES for questions:
        1. Generate exactly 10 questions.
        2. Questions 1-4 MUST be about specific projects mentioned in their resume (e.g., 'In your X project, how did you handle Y?').
        3. For technical tools like LangGraph, don't just ask 'Describe it'. Ask about a specific implementation detail like 'How did you handle state persistence across nodes?'.
        4. The 'expected_answer' must be a guide for a NON-TECHNICAL person. Example: 'Good signs: They mention "Checkpointers" or "Recursion limits". Ask them: "Did you use a persistent store for state?"'
        
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

    async def analyze_managerial_candidate(self, db: Session, candidate_id: int) -> Dict[str, Any]:
        """
        Analyzes resume, transcript, and feedback for managerial intelligence.
        Now includes Written Test scores and document download links.
        """
        # 1. Fetch Candidate Info
        cand_query = text("SELECT first_name, last_name, key_skills FROM candidate WHERE candidate_id = :id")
        cand = db.execute(cand_query, {"id": candidate_id}).fetchone()
        if not cand:
            raise Exception("Candidate not found")
        
        first_name, last_name, _ = cand

        # 2. Fetch Extra Fields (Written Test Score)
        score_query = text("SELECT value FROM extra_field WHERE data_item_id = :id AND field_name LIKE '%Written Test Score%'")
        score_row = db.execute(score_query, {"id": candidate_id}).fetchone()
        written_test_score = score_row[0] if score_row else None

        # 3. Fetch All Attachments
        att_query = text("""
            SELECT attachment_id, original_filename, directory_name, resume
            FROM attachment 
            WHERE data_item_id = :id AND data_item_type = 100
            ORDER BY date_created DESC
        """)
        attachments = db.execute(att_query, {"id": candidate_id}).fetchall()
        
        resume_text = ""
        transcript_text = ""
        feedback_text = ""
        
        transcript_id = None
        written_test_id = None
        feedback_id = None

        base_url = "http://172.16.1.40/paradigmitindia"

        async with httpx.AsyncClient() as client:
            for att_id, orig_filename, dir_name, is_resume in attachments:
                fname = orig_filename.lower()
                
                # Logic to categorize attachments
                is_transcript = any(word in fname for word in ["interview", "transcript", "l1", "ic", "screening"]) and "evaluation" not in fname and "form" not in fname
                is_written_test = any(word in fname for word in ["wt", "written", "test"])
                is_feedback = any(word in fname for word in ["evaluation", "form", "feedback", "feedback"])

                if (is_resume == 1 or not resume_text) and not is_transcript and not is_written_test and not is_feedback:
                    if not resume_text:
                        resume_text = await self._download_and_extract(client, base_url, att_id, dir_name, orig_filename)
                
                elif is_transcript:
                    transcript_id = att_id
                    if not transcript_text:
                        transcript_text = await self._download_and_extract(client, base_url, att_id, dir_name, orig_filename)
                
                elif is_written_test:
                    written_test_id = att_id
                
                elif is_feedback:
                    feedback_id = att_id
                    if not feedback_text:
                        feedback_text = await self._download_and_extract(client, base_url, att_id, dir_name, orig_filename)

        if not resume_text and not transcript_text:
            return {"error": "No resume or transcript found for analysis"}

        # 4. Prompt Gemini for Managerial Intelligence
        prompt = f"""
        You are a Senior Hiring Manager. Analyze the following Resume, Interview Transcript, and L1 Feedback for a candidate.
        Perform a cross-reference audit to help the Technical Manager prepare for the next round.
        
        CANDIDATE: {first_name} {last_name}
        WRITTEN TEST SCORE: {written_test_score if written_test_score else "N/A"}
        
        RESUME CONTENT:
        {resume_text[:5000]}
        
        INTERVIEW TRANSCRIPT (L1/Screening):
        {transcript_text[:6000] if transcript_text else "No transcript available."}
        
        L1 FEEDBACK/EVALUATION:
        {feedback_text[:4000] if feedback_text else "No specific feedback form text available."}
        
        Provide analysis in JSON format:
        {{
            "l1_summary": "Short executive summary of the L1 performance and feedback",
            "written_test_analysis": "Comment on their written test score of {written_test_score if written_test_score else 'N/A'}",
            "the_gap": ["List of inconsistencies between resume claims and interview/test performance"],
            "pain_points": ["Specific technical areas where the candidate struggled or was vague"],
            "strengths": ["Strongest areas confirmed by the interview/test"],
            "manager_strategy": [
                {{
                    "topic": "Topic Name",
                    "drill_down_question": "A deep-dive question for the manager to ask",
                    "why": "Reason why the manager needs to ask this"
                }}
            ]
        }}
        
        IMPORTANT: Be critical and direct. If the written test score is low or feedback mentioned 'poor communication', highlight it.
        """
        
        logger.info(f"Generating Deep Managerial Intelligence for {first_name} {last_name}")
        response = self.llm_service.llm.invoke(prompt)
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            analysis = json.loads(content)
            analysis["candidate_name"] = f"{first_name} {last_name}"
            analysis["written_test_score"] = written_test_score
            analysis["transcript_id"] = transcript_id
            analysis["written_test_id"] = written_test_id
            analysis["feedback_id"] = feedback_id
            
            # Helper for download URLs
            def get_dl_url(aid):
                if not aid: return None
                # Fetch directory name for hash
                dquery = text("SELECT directory_name FROM attachment WHERE attachment_id = :aid")
                drow = db.execute(dquery, {"aid": aid}).fetchone()
                if drow:
                    dhash = hashlib.md5(drow[0].encode()).hexdigest()
                    return f"{base_url}/index.php?m=attachments&a=getAttachment&id={aid}&directoryNameHash={dhash}"
                return None

            analysis["transcript_url"] = get_dl_url(transcript_id)
            analysis["written_test_url"] = get_dl_url(written_test_id)
            analysis["feedback_url"] = get_dl_url(feedback_id)

            return analysis
        except Exception as e:
            logger.error(f"Failed to parse Managerial analysis: {e}")
            return {"error": "Failed to parse Managerial analysis", "raw_content": content}

    async def _download_and_extract(self, client, base_url, att_id, dir_name, filename) -> str:
        try:
            dir_hash = hashlib.md5(dir_name.encode()).hexdigest()
            url = f"{base_url}/index.php?m=attachments&a=getAttachment&id={att_id}&directoryNameHash={dir_hash}"
            resp = await client.get(url, timeout=15.0)
            if resp.status_code == 200:
                return self.extract_text_from_file(resp.content, filename)
        except Exception as e:
            logger.error(f"Failed to download/extract {filename}: {e}")
        return ""

    def extract_text_from_file(self, content: bytes, filename: str) -> str:
        text = ""
        try:
            if filename.lower().endswith(".pdf"):
                reader = PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif filename.lower().endswith(".docx"):
                doc = docx.Document(io.BytesIO(content))
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                # Try raw text
                text = content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Extraction failed for {filename}: {e}")
        return text

    async def analyze_candidate_vs_jd(self, db: Session, resume_bytes: bytes, resume_name: str, jd_bytes: bytes, jd_name: str) -> Dict[str, Any]:
        """
        Analyzes a resume against a specific JD.
        """
        resume_text = self.extract_text_from_file(resume_bytes, resume_name)
        jd_text = self.extract_text_from_file(jd_bytes, jd_name)
        
        if not resume_text.strip() or not jd_text.strip():
            return {"error": "Failed to extract text from one or both files."}

        prompt = f"""
        You are a Senior Technical Recruiter. Analyze the following Resume against the provided Job Description (JD).
        Assess the match and provide a high-impact screening guide.
        
        JOB DESCRIPTION (JD):
        {jd_text[:5000]}
        
        CANDIDATE RESUME:
        {resume_text[:6000]}
        
        Provide analysis in JSON format:
        {{
            "match_score": "Score out of 100",
            "risk_analysis": ["bullet points of why the candidate might NOT fit this specific JD"],
            "strengths": ["bullet points of where the candidate perfectly aligns with the JD"],
            "missing_skills": ["Critical JD skills not found in the resume"],
            "initial_call_questions": [
                {{
                    "question": "The question text tailored to the JD requirements",
                    "expected_answer": "A 'Cheat Sheet' for HR. Give 2-3 specific keywords or technical terms the candidate MUST mention."
                }}
            ]
        }}
        
        IMPORTANT: Generate exactly 10 questions. Ensure at least 5 questions target the 'missing_skills' or 'risks' to see if the candidate actually has those skills despite they not being on the resume.
        """
        
        logger.info(f"Analyzing Resume vs JD: {resume_name} vs {jd_name}")
        response = self.llm_service.llm.invoke(prompt)
        content = response.content
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        try:
            analysis = json.loads(content)
            analysis["candidate_name"] = resume_name.split('.')[0]
            return analysis
        except Exception as e:
            return {"error": "Failed to parse Match analysis", "raw_content": content}

    async def analyze_candidate_file(self, db: Session, candidate_id: int, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyzes an uploaded PDF/Docx directly for a candidate.
        """
        # 1. Fetch Candidate Info
        cand = None
        if candidate_id > 0:
            cand_query = text("SELECT first_name, last_name, key_skills FROM candidate WHERE candidate_id = :id")
            cand = db.execute(cand_query, {"id": candidate_id}).fetchone()
        
        # 2. Extract Text from PDF
        text_content = self.extract_text_from_file(file_content, filename)

        if not text_content.strip():
            return {"error": "Extracted text is empty. Please ensure the PDF is not an image-only scan."}

        # 3. Prompt Gemini
        from datetime import datetime
        current_date = datetime.now().strftime("%d %B %Y")
        
        prompt = f"""
        You are an elite Technical Recruiter. Today's date is {current_date}.
        Analyze the following resume for a candidate.
        
        CANDIDATE: {cand[0] if cand else 'Unknown'} {cand[1] if cand else ''}
        
        RESUME CONTENT (EXTRACTED FROM UPLOADED PDF):
        {text_content}
        
        Provide a deep-dive analysis in the following JSON format:
        {{
            "risk_analysis": ["bullet points of potential risks, gaps, or concerns"],
            "strengths": ["bullet points of key technical and soft strengths"],
            "initial_call_questions": [
                {{
                    "question": "The question text",
                    "expected_answer": "A 'Cheat Sheet' for HR. Give 2-3 specific keywords or technical terms the candidate MUST mention. Add one simple 'Check' question the HR can ask to verify. DO NOT use generic phrases like 'should demonstrate understanding'."
                }}
            ]
        }}
        
        IMPORTANT RULES for questions:
        1. Generate exactly 10 questions.
        2. Questions 1-4 MUST be about specific projects mentioned in their resume (e.g., 'In your X project, how did you handle Y?').
        3. For technical tools like LangGraph, don't just ask 'Describe it'. Ask about a specific implementation detail like 'How did you handle state persistence across nodes?'.
        4. The 'expected_answer' must be a guide for a NON-TECHNICAL person. Example: 'Good signs: They mention "Checkpointers" or "Recursion limits". Ask them: "Did you use a persistent store for state?"'
        
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
