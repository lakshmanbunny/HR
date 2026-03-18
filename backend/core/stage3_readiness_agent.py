import json
import asyncio
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable
from core.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class Stage3ReadinessAgent:
    """
    Stage 3: Interview Readiness Agent.
    Synthesizes Stage 1 (Resume) and Stage 2 (GitHub) analysis to determine
    if a candidate is truly ready for a technical interview.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
            convert_system_message_to_human=True,
        )

    @traceable(name="Stage 3 - Interview Readiness Assessment")
    def evaluate(self, candidate_id: str, candidate_name: str, jd_text: str, stage1_data: Dict[str, Any], stage2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates interview readiness based on previous stage outputs.
        """
        logger.info(f"[STAGE 3] Running Readiness Assessment for {candidate_name} ({candidate_id})")

        system_prompt = """You are a Senior Technical Recruiter and Engineering Manager.
Your goal is to perform a final Interview Readiness Audit for a candidate.
You have access to their Resume Analysis (Stage 1) and their GitHub Code Review (Stage 2).

EVALUATION CRITERIA:
1. Technical Depth: Does their code match their resume claims?
2. Skills Gap: What is missing between their profile and the JD?
3. Confidence Score: How certain are you that this candidate will pass a live technical interview?
4. Focus Areas: Specific topics the interviewer should drill into.

RULES:
1. Every observation in the Executive Summary, Risk Factors, and Skill Gaps MUST include a citation.
2. Use [Resume] for citations from resume analysis.
3. Use [GitHub: reponame-filename] for citations from code analysis.

RESPONSE FORMAT (STRICT JSON — no markdown):
{
  "hire_readiness_level": "High" | "Medium" | "Low",
  "confidence_score": <int 0-100>,
  "risk_factors": [
    "⚠ <risk> [Citation]"
  ],
  "skill_gaps": [
    " <gap> [Citation]"
  ],
  "interview_focus_areas": [
    "🎯 <focus> [Citation]"
  ],
  "executive_summary": [
    "<key finding 1> [Citation]",
    "<key finding 2> [Citation]"
  ],
  "final_hiring_recommendation": "<brief recommendation string>"
}"""

        user_msg = f"""CANDIDATE: {candidate_name} ({candidate_id})

JOB DESCRIPTION:
{jd_text[:1500]}

STAGE 1: RESUME ANALYSIS
- Score: {stage1_data.get('resume_score', 'N/A')}
- Justification: {stage1_data.get('justification', [])}

STAGE 2: GITHUB CODE REVIEW
- GitHub Score: {stage2_data.get('github_score', 'N/A')}
- Justification: {stage2_data.get('github_justification', 'N/A')}
- Key Evidence: {json.dumps(stage2_data.get('ai_evidence', []), indent=2)}

Perform the final readiness audit. Return ONLY valid JSON."""

        try:
            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_msg),
                ],
                config={
                    "run_name": f"stage3-readiness-{candidate_id}",
                    "tags": ["stage3", "readiness-agent"],
                    "metadata": {"candidate_id": candidate_id, "candidate_name": candidate_name},
                },
            )
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            logger.info(f"[STAGE 3] {candidate_name} Readiness: {result.get('hire_readiness_level')} ({result.get('confidence_score')}%)")
            return result
        except Exception as e:
            logger.error(f"[STAGE 3] Readiness evaluation failed for {candidate_id}: {e}")
            return self._empty_result(str(e))

    async def evaluate_async(self, candidate_id: str, candidate_name: str, jd_text: str, stage1_data: Dict[str, Any], stage2_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async wrapper."""
        return await asyncio.to_thread(self.evaluate, candidate_id, candidate_name, jd_text, stage1_data, stage2_data)

    def _empty_result(self, reason: str) -> Dict[str, Any]:
        return {
            "hire_readiness_level": "Low",
            "confidence_score": 0,
            "risk_factors": [f"Evaluation Error: {reason}"],
            "skill_gaps": ["Unable to determine"],
            "interview_focus_areas": [],
            "executive_summary": f"Assessment failed: {reason}"
        }
