import json
import asyncio
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable
from core.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class Stage3SkepticAgent:
    """
    Stage 3: AI Skeptic Agent.
    Acts as an adversarial auditor to find reasons NOT to hire.
    Detects fluff, inconsistencies, and generic AI-generated code patterns.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True,
        )

    @traceable(name="Stage 3 - AI Skeptic Adversarial Audit")
    def evaluate(self, candidate_id: str, candidate_name: str, jd_text: str, stage1_data: Dict[str, Any], stage2_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates hiring risks and red flags.
        """
        logger.info(f"[STAGE 3] Running Skeptic Audit for {candidate_name} ({candidate_id})")

        system_prompt = """You are an Adversarial AI Auditor and Technical Skeptic.
Your job is to find reasons NOT to hire this candidate. You must be hyper-critical and look for:
1. Fluff & Buzzwords: Claims that aren't backed by code or specific experience.
2. Inconsistencies: Resume claims that contradict the complexity or quality of seen GitHub code.
3. Generic/AI Code: Patterns that suggest the GitHub code might be copied, generated, or simple tutorials.
4. Over-engineering: Complexity added where it wasn't needed.

RULE: Do NOT be mean, but do be EXTREMELY grounded. Avoid the 'hype'.
RULE: Every concern, risk, and observation MUST include a citation.
RULE: Use [Resume] for citations from resume analysis.
RULE: Use [GitHub: reponame-filename] for citations from code analysis.

RESPONSE FORMAT (STRICT JSON — no markdown):
{
  "risk_level": "High" | "Medium" | "Low",
  "major_concerns": [
    "⚠ <concern> [Citation]"
  ],
  "hidden_risks": [
    " <risk> [Citation]"
  ],
  "skeptic_recommendation": [
    "<auditor point 1> [Citation]",
    "<auditor point 2> [Citation]"
  ]
}"""

        user_msg = f"""CANDIDATE: {candidate_name} ({candidate_id})

JOB DESCRIPTION:
{jd_text[:1500]}

FULL EVALUATION DATA (STAGES 1 & 2):
Resume Score: {stage1_data.get('resume_score', 'N/A')}
GitHub Score: {stage2_data.get('github_score', 'N/A')}

Stage 1 Justification: {stage1_data.get('justification', [])}
Stage 2 Justification: {stage2_data.get('github_justification', 'N/A')}
Stage 2 Key Evidence: {json.dumps(stage2_data.get('ai_evidence', []), indent=2)}

Perform the adversarial audit. Return ONLY valid JSON."""

        try:
            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_msg),
                ],
                config={
                    "run_name": f"stage3-skeptic-{candidate_id}",
                    "tags": ["stage3", "skeptic-agent"],
                    "metadata": {"candidate_id": candidate_id, "candidate_name": candidate_name},
                },
            )
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            logger.info(f"[STAGE 3] {candidate_name} Skeptic Risk: {result.get('risk_level')}")
            return result
        except Exception as e:
            logger.error(f"[STAGE 3] Skeptic audit failed for {candidate_id}: {e}")
            return self._empty_result(str(e))

    async def evaluate_async(self, candidate_id: str, candidate_name: str, jd_text: str, stage1_data: Dict[str, Any], stage2_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async wrapper."""
        return await asyncio.to_thread(self.evaluate, candidate_id, candidate_name, jd_text, stage1_data, stage2_data)

    def _empty_result(self, reason: str) -> Dict[str, Any]:
        return {
            "risk_level": "High",
            "major_concerns": [f"Audit Error: {reason}"],
            "hidden_risks": ["Unable to fully assess due to error"],
            "skeptic_recommendation": f"Assessment failed: {reason}"
        }
