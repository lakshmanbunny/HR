import sys
import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

# Backend root (core, workflows, config live here)
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from core.settings import settings
from workflows.init_workflow import create_workflow
from config.logging_config import get_logger

import json
from fastapi.responses import StreamingResponse

from app.db.database import SessionLocal
from app.db import repository
from app.db.models import JobDescription, ScreeningResult
from core.stage2_github_agent import Stage2GitHubAgent
from core.stage3_readiness_agent import Stage3ReadinessAgent
from core.stage3_skeptic_agent import Stage3SkepticAgent

logger = get_logger(__name__)

class PipelineService:
    def __init__(self):
        self.workflow = create_workflow()
        logger.info("[PIPELINE] 3-Stage Funnel workflow initialized (Zero Embeddings)")

    def _ensure_list(self, data: Dict[str, Any], field: str):
        val = data.get(field)
        if isinstance(val, str):
            data[field] = [val]
        elif val is None:
            data[field] = []

    def _normalize_readiness(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not data or not isinstance(data, dict):
            return data
        
        self._ensure_list(data, "risk_factors")
        self._ensure_list(data, "skill_gaps")
        self._ensure_list(data, "interview_focus_areas")
        self._ensure_list(data, "executive_summary")
            
        if "final_hiring_recommendation" not in data:
            data["final_hiring_recommendation"] = "N/A"
            
        return data

    def _normalize_skeptic(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not data or not isinstance(data, dict):
            return data
        
        self._ensure_list(data, "major_concerns")
        self._ensure_list(data, "hidden_risks")
        self._ensure_list(data, "critical_skill_gaps")
        self._ensure_list(data, "skeptic_recommendation")
            
        return data

    async def _get_or_create_active_jd(self, db):
        jd = repository.get_active_jd(db)
        if not jd:
            jd_path = os.path.join(_BACKEND_ROOT, "NEW-JD")
            logger.info(f"No active JD found in DB. Reading from {jd_path}")
            try:
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
            except Exception as e:
                logger.error(f"Failed to read NEW-JD from {jd_path}: {e}")
                jd_text = "Fallback Job Description: AI Engineer"
            jd = repository.create_job_description(db, jd_text)
        return jd

    async def run_screening(self, force_eval: bool = False, target_candidate_id: Optional[str] = None, evaluation_weights: Optional[Dict[str, float]] = None, candidates: Optional[List[Dict[str, Any]]] = None, skip_llm_eval: bool = False) -> Dict[str, Any]:
        """
        Runs the full AI recruitment screening pipeline with smart caching.
        """
        db = SessionLocal()
        try:
            active_jd = await self._get_or_create_active_jd(db)
            
            # Identify candidates (Default to Woxsen candidates from DB if none provided)
            candidates_to_screen = candidates
            if candidates_to_screen is None:
                db_woxsen = repository.list_woxsen_candidates(db)
                candidates_to_screen = []
                for wc in db_woxsen:
                    candidates_to_screen.append({
                        "candidate_id": wc.roll_number,
                        "name": wc.name,
                        "email": wc.email,
                        "raw_resume_text": wc.raw_resume_text or "",
                        "links": {
                            "github": wc.github_url or "",
                            "linkedin": wc.linkedin_url or ""
                        }
                    })
            
            if not candidates_to_screen:
                raise ValueError("No candidates found in the woxsen_candidates database, and no external candidates were provided. Aborting screening.")
            
            all_cached = True
            cached_ranking = []
            cached_evaluations = {}
            
            # Helper for robust JSON loading
            def safe_json_load(val, default=None):
                if not val or val == '{}' or val == '[]':
                    return default
                try:
                    data = json.loads(val)
                    return data if data else default
                except:
                    return default

            # Check cache for partial updates (e.g force-evaluate 1 candidate)
            for res in candidates_to_screen:
                cand = repository.get_candidate_by_fuzzy_id(db, res['candidate_id'])
                if not cand:
                    all_cached = False
                    break
                    
                result = repository.get_screening_result(db, cand.id, active_jd.id)
                if not result:
                    all_cached = False
                    break

                cached_evaluations[res['candidate_id']] = {
                    "overall_score": int(result.overall_score or 0),
                    "resume_score": int(result.resume_score or 0),
                    "github_score": int(result.github_score or 0),
                    "repo_count": getattr(result, 'repo_count', 0) or 0,
                    "ai_projects": getattr(result, 'ai_projects', 0) or 0,
                    "justification": safe_json_load(getattr(result, 'justification_json', None), [result.recommendation] if result.recommendation else []),
                    "repos": safe_json_load(getattr(result, 'repos_json', None), []),
                    "interview_readiness": self._normalize_readiness(safe_json_load(getattr(result, 'interview_readiness_json', None))),
                    "skeptic_analysis": self._normalize_skeptic(safe_json_load(getattr(result, 'skeptic_analysis_json', None))),
                    "final_decision": result.recommendation,
                    "hr_decision": {
                        "decision": getattr(result, 'hr_decision', None),
                        "notes": getattr(result, 'hr_notes', None)
                    },
                    "ai_evidence": safe_json_load(getattr(result, 'ai_evidence_json', None), []),
                    "interview_status": getattr(result, 'interview_status', "PENDING"),
                    "evaluation_locked": getattr(result, 'evaluation_locked', False),
                    "interview_session_id": getattr(result, 'interview_session_id', None)
                }
                cached_ranking.append({
                    "candidate_id": res['candidate_id'],
                    "name": cand.name,
                    "score": result.overall_score,
                    "github_url": cand.github_url
                })

            if all_cached and cached_ranking and not force_eval:
                logger.info("[DB CACHE HIT] Returning results from database.")
                cached_ranking.sort(key=lambda x: x["score"], reverse=True)
                for idx, item in enumerate(cached_ranking, 1):
                    item["rank"] = idx
                return {
                    "ranking": cached_ranking,
                    "evaluations": cached_evaluations
                }



            logger.info(f"[PIPELINE] Invoking AI Recruitment Pipeline (Force Eval: {force_eval})")
            # Invoke the pipeline
            result = self.workflow.invoke({
                "message": "Starting 3-Stage Funnel screening...",
                "force_evaluation": force_eval,
                "target_candidate_id": target_candidate_id,
                "job_description": active_jd.jd_text,
                "resumes": candidates_to_screen,
            })
            
            # Extract and Format results — 3-Stage Funnel
            ranking_results = result.get("ranking_results", [])
            stage_1_results = result.get("stage_1_results", {})
            llm_evaluations = result.get("llm_evaluations", {})
            github_raw_data = result.get("github_raw_data", {})
            github_features = result.get("github_features", {})
            github_code_files = result.get("github_code_files", {})
            interview_readiness = result.get("interview_readiness", {})
            skeptic_analysis = result.get("skeptic_analysis", {})
            
            # Save candidates and results to DB
            logger.info("[SAVING SCREENING RESULT] Persisting 3-Stage Funnel results to database.")

            formatted_ranking = []
            formatted_evaluations = {}
            
            for idx, item in enumerate(ranking_results, 1):
                cand_id = item["candidate_id"]
                
                # If target_candidate_id was provided and this is NOT the target candidate,
                # we preserve their existing data from the database cache
                if force_eval and target_candidate_id and cand_id.lower() != target_candidate_id.lower():
                    if cand_id in cached_evaluations:
                        formatted_evaluations[cand_id] = cached_evaluations[cand_id]
                        cached_item = next((r for r in cached_ranking if r["candidate_id"] == cand_id), None)
                        if cached_item:
                            formatted_ranking.append(cached_item)
                    continue

                stage_1_data = stage_1_results.get(cand_id, {})
                eval_data = llm_evaluations.get(cand_id, {})
                gh_feat = github_features.get(cand_id, {})
                readiness_data = interview_readiness.get(cand_id, {})
                skeptic_data = skeptic_analysis.get(cand_id, {})
                
                # Stage 1 scores
                s1_scores = stage_1_data.get("stage_1_scores", {})
                base_score = s1_scores.get("base_score", 0.0)
                coverage = s1_scores.get("coverage_score", 0.0)
                similarity = s1_scores.get("similarity_score", 0.0)
                
                # Get resume for metadata
                resume_obj = next((r for r in candidates_to_screen if r["candidate_id"] == cand_id), {})
                email = resume_obj.get("email") or f"{cand_id.lower()}@example.com"
                linkedin_url = resume_obj.get("links", {}).get("linkedin", "")
                
                # Create/Get Candidate
                db_cand = repository.get_candidate_by_email(db, email)
                if not db_cand:
                    db_cand = repository.create_candidate(
                        db, 
                        name=resume_obj.get("name", cand_id),
                        email=email,
                        github_url=resume_obj.get("links", {}).get("github", ""),
                        linkedin_url=linkedin_url
                    )
                else:
                    db_cand.github_url = resume_obj.get("links", {}).get("github", "")
                    db_cand.linkedin_url = linkedin_url
                    db.commit()
                
                # Use Stage 3 overall_score if available, otherwise Stage 1 base_score
                overall_score = eval_data.get("overall_score") if eval_data.get("overall_score") else int(base_score)
                
                # Combine hiring justification from Stage 1 and Stage 3
                justification = eval_data.get("justification", [])
                if not justification:
                    justification = stage_1_data.get("hiring_justification", [])
                
                # Recommendation from skeptic or readiness data
                recommendation = "PROCEED WITH CAUTION"
                if readiness_data and readiness_data.get("readiness_level"):
                    recommendation = readiness_data.get("readiness_level", "PROCEED WITH CAUTION")
                
                res_data = {
                    "resume_score": eval_data.get("resume_score") or int(coverage),
                    "github_score": eval_data.get("github_score", 0),
                    "overall_score": overall_score,
                    "risk_level": skeptic_data.get("risk_level", "LOW") if skeptic_data else "LOW",
                    "readiness_level": readiness_data.get("readiness_level", "MEDIUM") if readiness_data else "MEDIUM",
                    "recommendation": recommendation,
                    "repo_count": github_raw_data.get(cand_id, {}).get("total_repos", 0),
                    "ai_projects": len(github_raw_data.get(cand_id, {}).get("ai_relevant_repos", [])),
                    "skill_gaps": readiness_data.get("skill_gaps", []) if readiness_data else [],
                    "interview_focus": readiness_data.get("interview_focus", []) if readiness_data else [],
                    "github_features": gh_feat,
                    "repos": github_code_files.get(cand_id, {}).get("repos", []),
                    "interview_readiness": readiness_data if readiness_data else None,
                    "skeptic_analysis": skeptic_data if skeptic_data else None,
                    "ai_evidence": eval_data.get("ai_evidence", []),
                    "justification": justification,
                    "rank_position": idx,
                    "retrieval_mode": "flash_single_pass",
                    "retrieval_version": "v3_funnel",
                    "rag_enabled": True,
                    "rag_status": "healthy",
                    "rag_quality_status": "HEALTHY",
                    "rag_quality_score": base_score / 100.0,
                    "rag_override": False,
                    "judge_audit": eval_data.get("judge_audit", {}),
                    "rubric_scores": eval_data.get("rubric_scores", {}),
                    # Stage 1 specific data
                    "stage_1_coverage": coverage,
                    "stage_1_similarity": similarity,
                    "stage_1_base_score": base_score,
                    "stage_1_justification": stage_1_data.get("stage_1_justification", ""),
                }
                
                # Save to DB
                saved_res = repository.save_screening_result(db, db_cand.id, active_jd.id, res_data)

                # Save Stage 1 metrics as RAG metrics (for compatibility with existing frontend)
                stage1_metrics = {
                    "coverage": coverage / 100.0,
                    "similarity": similarity / 100.0,
                    "diversity": 0.0,  # Not applicable in new architecture
                    "density": 0.0,    # Not applicable in new architecture
                    "overall_rag_score": base_score / 100.0,
                    "rag_health_status": "HEALTHY",
                    "chunk_count": 0,
                    "jd_coverage_pct": coverage / 100.0,
                }
                try:
                    repository.save_rag_retrieval_metrics(db, db_cand.id, stage1_metrics)
                except Exception as e:
                    logger.error(f"Failed to save Stage 1 metrics for {cand_id}: {str(e)}")
                
                # Format for API
                formatted_ranking.append({
                    "candidate_id": cand_id,
                    "name": db_cand.name,
                    "score": overall_score,
                    "github_url": db_cand.github_url
                })
                
                formatted_evaluations[cand_id] = {
                    "overall_score": overall_score,
                    "resume_score": int(eval_data.get("resume_score", 0)) or int(coverage),
                    "github_score": int(eval_data.get("github_score", 0)),
                    "repo_count": github_raw_data.get(cand_id, {}).get("total_repos", 0),
                    "ai_projects": len(github_raw_data.get(cand_id, {}).get("ai_relevant_repos", [])),
                    "justification": justification,
                    "repos": github_code_files.get(cand_id, {}).get("repos", []),
                    "interview_readiness": readiness_data if readiness_data else None,
                    "skeptic_analysis": skeptic_data if skeptic_data else None,
                    "final_decision": recommendation,
                    "hr_decision": {
                        "decision": saved_res.hr_decision,
                        "notes": saved_res.hr_notes
                    },
                    "ai_evidence": eval_data.get("ai_evidence", []),
                    "evaluation_blocked": False,
                    "judge_audit": eval_data.get("judge_audit"),
                    "rubric_scores": eval_data.get("rubric_scores"),
                    "interview_status": "PENDING",
                    "evaluation_locked": False,
                    "interview_session_id": None,
                    "rag_override": False,
                    # Stage 1 data for frontend
                    "stage_1_scores": s1_scores,
                    "stage_1_justification": stage_1_data.get("stage_1_justification", ""),
                    "hiring_justification": stage_1_data.get("hiring_justification", []),
                }
            formatted_ranking.sort(key=lambda x: x["score"], reverse=True)
            for i, rank_item in enumerate(formatted_ranking, 1):
                rank_item["rank"] = i
            
            return {
                "ranking": formatted_ranking,
                "evaluations": formatted_evaluations
            }
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise e
        finally:
            db.close()

    async def run_bulk_screening(self, file_path: str, evaluation_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Ingests candidates from a file and runs screening for them.
        """
        from app.services.data_ingestion import data_ingestion_service
        logger.info(f"[PIPELINE] Bulk screening triggered for file: {file_path}")
        
        candidates = data_ingestion_service.parse_file(file_path)
        return await self.run_screening(candidates=candidates, evaluation_weights=evaluation_weights)

    async def force_evaluate(self, candidate_id: str, evaluation_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Force-run the pipeline by bypassing RAG quality gate.
        Resolves candidate_id (GitHub username, roll number, or DB ID) to the canonical
        roll_number so that the workflow's target_candidate_id matches ranking_results cand_id.
        """
        logger.info(f"[API] Force evaluating candidate: {candidate_id}")
        db = SessionLocal()
        try:
            # Resolve any fuzzy ID (GitHub username, email, etc.) → canonical roll number
            cand = repository.get_candidate_by_fuzzy_id(db, candidate_id)
            if cand:
                # Get associated WoxsenCandidate to find roll_number (used as cand_id in ranking)
                from app.db.models import WoxsenCandidate
                wc = db.query(WoxsenCandidate).filter(WoxsenCandidate.email == cand.email).first()
                resolved_id = wc.roll_number if wc else candidate_id
                logger.info(f"[FORCE EVAL] Resolved '{candidate_id}' → '{resolved_id}'")
            else:
                resolved_id = candidate_id
                logger.warning(f"[FORCE EVAL] Could not resolve '{candidate_id}', using as-is.")
        finally:
            db.close()

        return await self.run_screening(force_eval=True, target_candidate_id=resolved_id, evaluation_weights=evaluation_weights)

    async def toggle_rag_override(self, candidate_id: str, override: bool) -> Dict[str, Any]:
        """
        Toggles the quality-gate override on a candidate's latest screening result.
        """
        db = SessionLocal()
        try:
            cand = repository.get_candidate_by_fuzzy_id(db, candidate_id)
            if not cand:
                raise Exception("Candidate not found")

            jd = await self._get_or_create_active_jd(db)
            result = repository.get_screening_result(db, cand.id, jd.id)
            if not result:
                raise Exception("Screening result not found")

            updated = repository.update_rag_override(db, result.id, override)

            if override:
                logger.warning(f"[OVERRIDE] HR override applied for {candidate_id}")

            return {"candidate_id": candidate_id, "rag_override": updated.rag_override if updated else override}
        finally:
            db.close()

    async def get_candidate_rag_metrics(self, candidate_id: str) -> Dict[str, Any]:
        """Stage-1 retrieval-style metrics (JD coverage, similarity, etc.)."""
        db = SessionLocal()
        try:
            cand = repository.get_candidate_by_fuzzy_id(db, candidate_id)
            if not cand:
                raise Exception(f"Candidate {candidate_id} not found")

            metrics = repository.get_rag_retrieval_metrics(db, cand.id)
            if metrics:
                return {
                    "candidate_id": candidate_id,
                    "coverage": metrics.coverage,
                    "similarity": metrics.similarity,
                    "diversity": metrics.diversity,
                    "density": metrics.density,
                    "overall_score": metrics.overall_score,
                    "health_status": metrics.rag_health_status,
                    "source": "stage1_metrics",
                }

            legacy = repository.get_rag_metrics(db, cand.id)
            if legacy:
                return {
                    "candidate_id": candidate_id,
                    "retrieval_score": legacy.retrieval_score,
                    "coverage_score": legacy.coverage_score,
                    "source": "legacy_rag_metric",
                }
            return {"candidate_id": candidate_id, "error": "No metrics found"}
        finally:
            db.close()

    async def get_rag_run_summary(self) -> Dict[str, Any]:
        """Aggregate Stage-1 metric health across candidates with retrieval records."""
        db = SessionLocal()
        try:
            all_m = repository.list_all_rag_retrieval_metrics(db)
            if not all_m:
                return {"total_candidates": 0, "message": "No stage-1 metrics found."}

            healthy = sum(1 for m in all_m if (m.rag_health_status or "").upper() == "HEALTHY")
            scores = [m.overall_score for m in all_m if m.overall_score is not None]
            avg = round(sum(scores) / len(scores), 4) if scores else 0.0
            return {
                "total_candidates": len(all_m),
                "healthy_count": healthy,
                "average_overall_score": avg,
                "average_coverage": round(sum(m.coverage or 0 for m in all_m) / len(all_m), 4),
                "average_similarity": round(sum(m.similarity or 0 for m in all_m) / len(all_m), 4),
            }
        finally:
            db.close()


    async def re_evaluate(self, candidate_id: str) -> Dict[str, Any]:
        """
        Deletes existing result and re-runs the pipeline.
        """
        db = SessionLocal()
        try:
            active_jd = await self._get_or_create_active_jd(db)
            target_cand = repository.get_candidate_by_fuzzy_id(db, candidate_id)
            
            if target_cand:
                repository.delete_screening_result(db, target_cand.id, active_jd.id)
            
            return await self.run_screening()
        finally:
            db.close()

    async def get_stored_results(self) -> Dict[str, Any]:
        """
        Fetches existing results from DB. Returns empty data if nothing found.
        """
        db = SessionLocal()
        try:
            active_jd = await self._get_or_create_active_jd(db)
            stage2_results = repository.list_screening_results(db, active_jd.id)

            # Helper for robust JSON loading
            def safe_json_load(val, default=None):
                if not val or val == '{}' or val == '[]':
                    return default
                try:
                    data = json.loads(val)
                    return data if data else default
                except:
                    return default

            formatted_ranking = []
            formatted_evaluations = {}
            stage2_candidate_ids = set()

            # --- Phase 1: Build Stage 2 (LLM-evaluated) entries ---
            sorted_stage2 = sorted(stage2_results, key=lambda x: (x.overall_score or 0.0, -(x.rank_position or 9999)), reverse=True)
            for idx, res in enumerate(sorted_stage2, 1):
                cand = res.candidate
                from app.db.models import WoxsenCandidate
                wc = db.query(WoxsenCandidate).filter(WoxsenCandidate.email == cand.email).first()
                cand_id = wc.roll_number if wc else cand.email.split('@')[0].upper()
                stage2_candidate_ids.add(cand.id)

                metric_rec = repository.get_rag_retrieval_metrics(db, cand.id)
                metrics = {}
                if metric_rec:
                    metrics = {
                        "coverage": metric_rec.coverage,
                        "similarity": metric_rec.similarity,
                        "diversity": metric_rec.diversity,
                        "density": metric_rec.density,
                        "overall_score": metric_rec.overall_score
                    }

                formatted_ranking.append({
                    "rank": idx,
                    "candidate_id": cand_id,
                    "name": cand.name,
                    "score": res.overall_score,
                    "github_url": cand.github_url
                })

                formatted_evaluations[cand_id] = {
                    "overall_score": int(res.overall_score or 0),
                    "resume_score": int(res.resume_score or 0),
                    "github_score": int(res.github_score or 0),
                    "precision_score": int(metrics.get("precision_score", 0)),
                    "recall_score": int(metrics.get("recall_score", 0)),
                    "repo_count": getattr(res, 'repo_count', 0) or 0,
                    "ai_projects": getattr(res, 'ai_projects', 0) or 0,
                    "justification": safe_json_load(getattr(res, 'justification_json', None), [res.recommendation] if res.recommendation else []),
                    "repos": safe_json_load(getattr(res, 'repos_json', None), []),
                    "interview_readiness": self._normalize_readiness(safe_json_load(getattr(res, 'interview_readiness_json', None))),
                    "skeptic_analysis": self._normalize_skeptic(safe_json_load(getattr(res, 'skeptic_analysis_json', None))),
                    "final_decision": res.recommendation,
                    "final_synthesized_decision": safe_json_load(getattr(res, 'final_synthesized_decision_json', None)),
                    "hr_decision": {
                        "decision": res.hr_decision,
                        "notes": res.hr_notes,
                        "status": "COMPLETED" if res.hr_decision else "PENDING"
                    },
                    "ai_evidence": safe_json_load(getattr(res, 'ai_evidence_json', None), []),
                    "code_evidence": safe_json_load(getattr(res, 'ai_evidence_json', None), []),
                    "judge_audit": safe_json_load(getattr(res, 'judge_audit_json', None)),
                    "rubric_scores": safe_json_load(getattr(res, 'rubric_scores_json', None)),
                    "rag_quality": {
                        "status": getattr(res, 'rag_status', 'CRITICAL') or 'CRITICAL',
                        "score": metrics.get("overall_score", 0.0),
                        "metrics": metrics
                    },
                    "evaluation_blocked": (getattr(res, 'rag_status', 'CRITICAL') != "healthy") and not getattr(res, 'rag_override', False),
                    "raw_resume_text": wc.raw_resume_text if wc else "",
                    "github_features": safe_json_load(getattr(res, 'github_features_json', None), {}),
                    "stage": "stage2"
                }

                # Extract parsed GitHub rubric fields for direct frontend access
                gh_features = formatted_evaluations[cand_id].get("github_features") or {}
                if isinstance(gh_features, dict) and gh_features.get("rubric_scores"):
                    formatted_evaluations[cand_id]["github_rubric"] = gh_features.get("rubric_scores", {})
                    formatted_evaluations[cand_id]["github_strengths"] = gh_features.get("strengths", [])
                    formatted_evaluations[cand_id]["github_weaknesses"] = gh_features.get("weaknesses", [])
                    formatted_evaluations[cand_id]["github_justification"] = gh_features.get("github_justification", "")

            # --- Phase 2: Append Stage 1-only candidates (not shortlisted for Stage 2) ---
            all_stage1 = repository.list_all_rag_retrieval_metrics(db)
            stage1_only = [m for m in all_stage1 if m.candidate_id not in stage2_candidate_ids]

            stage2_count = len(formatted_ranking)
            for idx, m in enumerate(stage1_only, stage2_count + 1):
                cand = m.candidate
                from app.db.models import WoxsenCandidate
                wc = db.query(WoxsenCandidate).filter(WoxsenCandidate.email == cand.email).first()
                cand_id = wc.roll_number if wc else cand.email.split('@')[0].upper()


                metrics = {
                    "coverage": m.coverage,
                    "similarity": m.similarity,
                    "diversity": m.diversity,
                    "density": m.density,
                    "overall_score": m.overall_score
                }

                formatted_ranking.append({
                    "rank": idx,
                    "candidate_id": cand_id,
                    "name": cand.name,
                    "score": 0,  # No Stage 2 score
                    "github_url": cand.github_url
                })

                formatted_evaluations[cand_id] = {
                    "overall_score": 0,
                    "resume_score": 0,
                    "github_score": 0,
                    "precision_score": 0,
                    "recall_score": 0,
                    "repo_count": 0,
                    "ai_projects": 0,
                    "justification": [],
                    "repos": [],
                    "interview_readiness": None,
                    "skeptic_analysis": None,
                    "final_decision": "PENDING DEEP EVALUATION",
                    "final_synthesized_decision": None,
                    "hr_decision": {"decision": None, "notes": None, "status": "PENDING"},
                    "ai_evidence": [],
                    "judge_audit": None,
                    "rubric_scores": None,
                    "rag_quality": {
                        "status": m.rag_health_status,
                        "score": m.overall_score,
                        "metrics": metrics
                    },
                    "evaluation_blocked": m.rag_health_status != "HEALTHY",
                    "stage": "stage1_only"
                }

            return {
                "ranking": formatted_ranking,
                "evaluations": formatted_evaluations
            }
        finally:
            db.close()

    async def run_screening_stream(self, evaluation_weights: Optional[Dict[str, float]] = None):
        """
        Real-time streaming pipeline with batch-of-5 processing.
        Yields incremental NDJSON results as each batch completes.
        """
        import json
        from core.stage1_flash_scorer import Stage1FlashScorer
        from core.github_verifier import GitHubVerifier
        from core.llm_service import LLMService

        BATCH_SIZE = 5
        FUNNEL_THRESHOLD = 60

        db = SessionLocal()
        try:
            active_jd = await self._get_or_create_active_jd(db)
            jd_text = active_jd.jd_text

            # Load candidates from DB
            db_woxsen = repository.list_woxsen_candidates(db)
            candidates = []
            for wc in db_woxsen:
                candidates.append({
                    "candidate_id": wc.roll_number,
                    "name": wc.name,
                    "email": wc.email,
                    "raw_resume_text": wc.raw_resume_text or "",
                    "links": {
                        "github": wc.github_url or "",
                        "linkedin": wc.linkedin_url or ""
                    }
                })

            total = len(candidates)
            yield json.dumps({"step": 0, "status": "System Initialization", "total_candidates": total}) + "\n"
            await asyncio.sleep(0.1)
            yield json.dumps({"step": 1, "status": f"Loading {total} candidates"}) + "\n"
            await asyncio.sleep(0.1)

            # ================================================================
            # STAGE 1: Flash Scoring — Batch of 5, stream after each batch
            # ================================================================
            yield json.dumps({"step": 2, "status": "Stage 1: Flash Extraction & Scoring"}) + "\n"

            scorer = Stage1FlashScorer()
            stage_1_results = {}
            all_ranking = []
            all_evaluations = {}

            # Process in batches of 5
            for batch_start in range(0, total, BATCH_SIZE):
                batch = candidates[batch_start:batch_start + BATCH_SIZE]
                batch_num = (batch_start // BATCH_SIZE) + 1
                total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

                logger.info(f"[STAGE 1] Batch {batch_num}/{total_batches} — scoring {len(batch)} candidates")

                # Run batch concurrently
                tasks = []
                for cand in batch:
                    tasks.append(scorer.score_candidate_async(
                        candidate_id=cand["candidate_id"],
                        resume_json=cand.get("raw_resume_text", ""),
                        job_description=jd_text
                    ))

                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process batch results
                for cand, result in zip(batch, batch_results):
                    cand_id = cand["candidate_id"]

                    if isinstance(result, Exception):
                        logger.error(f"[STAGE 1] Error for {cand_id}: {result}")
                        result = {
                            "stage_1_scores": {"coverage_score": 0, "similarity_score": 0, "base_score": 0},
                            "stage_1_justification": f"Error: {result}",
                            "hiring_justification": [f"🔴 Scoring failed: {result}"],
                            "extracted_skills": [],
                            "experience_level": "Unknown",
                            "domain_match": "None"
                        }

                    stage_1_results[cand_id] = result
                    s1_scores = result.get("stage_1_scores", {})
                    base_score = s1_scores.get("base_score", 0.0)

                    # Save candidate to DB
                    email = cand.get("email") or f"{cand_id.lower()}@example.com"
                    db_cand = repository.get_candidate_by_email(db, email)
                    if not db_cand:
                        db_cand = repository.create_candidate(
                            db,
                            name=cand.get("name", cand_id),
                            email=email,
                            github_url=cand.get("links", {}).get("github", ""),
                            linkedin_url=cand.get("links", {}).get("linkedin", "")
                        )

                    all_ranking.append({
                        "candidate_id": cand_id,
                        "name": cand.get("name", cand_id),
                        "score": int(base_score),
                        "github_url": cand.get("links", {}).get("github", "")
                    })

                    all_evaluations[cand_id] = {
                        "overall_score": int(base_score),
                        "resume_score": int(s1_scores.get("coverage_score", 0)),
                        "github_score": 0,
                        "repo_count": 0,
                        "ai_projects": 0,
                        "justification": result.get("hiring_justification", []),
                        "repos": [],
                        "interview_readiness": None,
                        "skeptic_analysis": None,
                        "final_decision": "STAGE 1 SCORED",
                        "hr_decision": {"decision": None, "notes": None},
                        "ai_evidence": [],
                        "evaluation_blocked": False,
                        "judge_audit": None,
                        "rubric_scores": None,
                        "interview_status": "PENDING",
                        "evaluation_locked": False,
                        "interview_session_id": None,
                        "rag_override": False,
                        "stage_1_scores": s1_scores,
                        "stage_1_justification": result.get("stage_1_justification", ""),
                        "hiring_justification": result.get("hiring_justification", []),
                        "raw_resume_text": cand.get("raw_resume_text", ""),
                    }

                # Sort ranking after each batch and stream
                all_ranking.sort(key=lambda x: x["score"], reverse=True)
                for i, r in enumerate(all_ranking, 1):
                    r["rank"] = i

                yield json.dumps({
                    "step": 2,
                    "status": f"Stage 1: Scored {min(batch_start + BATCH_SIZE, total)}/{total} candidates",
                    "partial_results": {
                        "ranking": all_ranking,
                        "evaluations": all_evaluations
                    }
                }) + "\n"

            # ================================================================
            # FINALIZE: Save all Stage 1 results to DB
            # ================================================================
            yield json.dumps({"step": 3, "status": "Saving Stage 1 results to database"}) + "\n"

            for cand in candidates:
                cand_id = cand["candidate_id"]
                email = cand.get("email") or f"{cand_id.lower()}@example.com"
                db_cand = repository.get_candidate_by_email(db, email)
                if db_cand:
                    s1 = stage_1_results.get(cand_id, {})
                    s1_scores = s1.get("stage_1_scores", {})
                    res_data = {
                        "resume_score": int(s1_scores.get("coverage_score", 0)),
                        "github_score": 0,
                        "overall_score": int(s1_scores.get("base_score", 0)),
                        "risk_level": "PENDING",
                        "readiness_level": "PENDING",
                        "recommendation": "STAGE 1 SCORED",
                        "repo_count": 0,
                        "ai_projects": 0,
                        "skill_gaps": [],
                        "interview_focus": [],
                        "github_features": {},
                        "repos": [],
                        "interview_readiness": None,
                        "skeptic_analysis": None,
                        "ai_evidence": [],
                        "justification": s1.get("hiring_justification", []),
                        "rank_position": next((r["rank"] for r in all_ranking if r["candidate_id"] == cand_id), 0),
                        "retrieval_mode": "flash_single_pass",
                        "retrieval_version": "v3_funnel",
                        "rag_enabled": True,
                        "rag_status": "healthy",
                        "rag_quality_status": "HEALTHY",
                        "rag_quality_score": s1_scores.get("base_score", 0) / 100.0,
                        "rag_override": False,
                        "judge_audit": {},
                        "rubric_scores": {},
                        "stage_1_coverage": s1_scores.get("coverage_score", 0),
                        "stage_1_similarity": s1_scores.get("similarity_score", 0),
                        "stage_1_base_score": s1_scores.get("base_score", 0),
                        "stage_1_justification": s1.get("stage_1_justification", ""),
                    }
                    try:
                        repository.save_screening_result(db, db_cand.id, active_jd.id, res_data)
                    except Exception as e:
                        logger.error(f"[DB] Failed to save result for {cand_id}: {e}")

            # Final results
            all_ranking.sort(key=lambda x: x["score"], reverse=True)
            for i, r in enumerate(all_ranking, 1):
                r["rank"] = i

            final_results = {
                "ranking": all_ranking,
                "evaluations": all_evaluations
            }

            yield json.dumps({"step": 6, "results": final_results}) + "\n"
            logger.info(f"[STREAM] Stage 1 complete. {total} candidates scored.")

        except Exception as e:
            logger.error(f"[STREAM] Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            yield json.dumps({"error": str(e)}) + "\n"
        finally:
            db.close()

    # ================================================================
    # STAGE 2: GitHub Verification — Manually Triggered
    # ================================================================
    async def run_stage_2_stream(self):
        """
        Stream Stage 2 GitHub verification for Top 60 candidates.
        Processes in batches of 5, yields NDJSON with partial_results.
        """
        from core.stage2_github_agent import Stage2GitHubAgent
        from app.db.models import WoxsenCandidate

        BATCH_SIZE = 5
        TOP_N = 60

        db = SessionLocal()
        try:
            yield json.dumps({"step": 0, "status": "Loading Stage 1 results..."}) + "\n"

            active_jd = await self._get_or_create_active_jd(db)
            jd_text = active_jd.jd_text

            # Load Top 60 by overall_score
            all_results = repository.list_screening_results(db, active_jd.id)
            sorted_results = sorted(all_results, key=lambda x: (x.overall_score or 0), reverse=True)
            top_results = sorted_results[:TOP_N]

            if not top_results:
                yield json.dumps({"error": "No Stage 1 results found. Run Stage 1 first."}) + "\n"
                return

            logger.info(f"[STAGE 2] Starting GitHub verification for {len(top_results)} candidates")

            agent = Stage2GitHubAgent()
            total = len(top_results)
            all_ranking = []
            all_evaluations = {}

            # Build initial ranking from existing DB data
            for idx, res in enumerate(top_results, 1):
                cand = res.candidate
                wc = db.query(WoxsenCandidate).filter(WoxsenCandidate.email == cand.email).first()
                cand_id = wc.roll_number if wc else cand.email.split("@")[0].upper()
                github_url = cand.github_url or (wc.github_url if wc else "")

                all_ranking.append({
                    "rank": idx,
                    "candidate_id": cand_id,
                    "name": cand.name,
                    "score": int(res.overall_score or 0),
                    "github_url": github_url,
                })
                all_evaluations[cand_id] = {
                    "candidate_id": cand_id,
                    "db_candidate_id": cand.id,
                    "db_result_id": res.id,
                    "github_url": github_url,
                    "overall_score": int(res.overall_score or 0),
                    "resume_score": int(res.resume_score or 0),
                    "github_score": int(res.github_score or 0),
                    "justification": json.loads(res.justification_json) if res.justification_json else [],
                    "raw_resume_text": wc.raw_resume_text if wc else "",
                }

            yield json.dumps({
                "step": 1,
                "status": f"Stage 2: GitHub Verification for Top {total} candidates",
                "partial_results": {"ranking": all_ranking, "evaluations": all_evaluations},
            }) + "\n"

            # Process in batches
            for batch_start in range(0, total, BATCH_SIZE):
                batch = list(all_evaluations.items())[batch_start:batch_start + BATCH_SIZE]
                batch_num = (batch_start // BATCH_SIZE) + 1
                total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

                logger.info(f"[STAGE 2] Batch {batch_num}/{total_batches}")
                yield json.dumps({
                    "step": 2,
                    "status": f"Stage 2: Batch {batch_num}/{total_batches} — Analyzing GitHub profiles",
                }) + "\n"

                # Run batch concurrently
                tasks = []
                for cand_id, eval_data in batch:
                    github_url = eval_data.get("github_url", "")
                    tasks.append(agent.evaluate_async(cand_id, github_url, jd_text))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for (cand_id, eval_data), result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(f"[STAGE 2] Exception for {cand_id}: {result}")
                        result = agent._empty_result(str(result))

                    gh_score = result.get("github_score", 0)
                    stage1_score = eval_data.get("resume_score", 0)
                    # Combined: 60% resume + 40% github
                    combined = int(stage1_score * 0.6 + gh_score * 0.4)

                    all_evaluations[cand_id].update({
                        "github_score": gh_score,
                        "overall_score": combined,
                        "repo_count": result.get("repo_count", 0),
                        "ai_projects": result.get("ai_projects", 0),
                        "repos": result.get("repos", []),
                        "code_evidence": result.get("code_evidence", []),
                        "github_rubric": result.get("rubric_scores", {}),
                        "github_strengths": result.get("strengths", []),
                        "github_weaknesses": result.get("weaknesses", []),
                        "github_justification": result.get("github_justification", ""),
                    })

                    # Update ranking score
                    for r in all_ranking:
                        if r["candidate_id"] == cand_id:
                            r["score"] = combined
                            break

                    # Persist to DB — update the existing screening_result row
                    try:
                        existing = db.query(ScreeningResult).get(eval_data["db_result_id"])
                        if existing:
                            existing.github_score = gh_score
                            existing.overall_score = combined
                            existing.repo_count = result.get("repo_count", 0)
                            existing.ai_projects = result.get("ai_projects", 0)
                            existing.repos_json = json.dumps(result.get("repos", []))
                            existing.ai_evidence_json = json.dumps(result.get("code_evidence", []))
                            existing.github_features_json = json.dumps({
                                "rubric_scores": result.get("rubric_scores", {}),
                                "strengths": result.get("strengths", []),
                                "weaknesses": result.get("weaknesses", []),
                                "github_justification": result.get("github_justification", ""),
                                "github_username": result.get("github_username"),
                            })
                            db.commit()
                    except Exception as e:
                        logger.error(f"[STAGE 2] DB update failed for {cand_id}: {e}")
                        db.rollback()

                # Re-sort and stream after each batch
                all_ranking.sort(key=lambda x: x["score"], reverse=True)
                for i, r in enumerate(all_ranking, 1):
                    r["rank"] = i

                yield json.dumps({
                    "step": 2,
                    "status": f"Stage 2: {min(batch_start + BATCH_SIZE, total)}/{total} candidates verified",
                    "partial_results": {"ranking": all_ranking, "evaluations": all_evaluations},
                }) + "\n"

            # Final results
            yield json.dumps({
                "step": 6,
                "results": {"ranking": all_ranking, "evaluations": all_evaluations},
            }) + "\n"
            logger.info(f"[STAGE 2] Complete. {total} candidates GitHub-verified.")

        except Exception as e:
            logger.error(f"[STAGE 2] Pipeline error: {str(e)}")
            import traceback
            traceback.print_exc()
            yield json.dumps({"error": str(e)}) + "\n"
        finally:
            db.close()

    async def submit_hr_decision(self, request: Any) -> Dict[str, Any]:
        """
        Persists HR decision to DB and returns the decision object for UI sync.
        """
        db = SessionLocal()
        try:
            active_jd = await self._get_or_create_active_jd(db)
            
            # Find candidate using robust fuzzy lookup
            target_cand = repository.get_candidate_by_fuzzy_id(db, request.candidate_id)
            
            if not target_cand:
                logger.error(f"Candidate not found for decision: {request.candidate_id}")
                raise Exception("Candidate not found")

            # Persist decision
            repository.update_screening_hr_decision(
                db, 
                target_cand.id, 
                active_jd.id, 
                request.decision, 
                request.notes
            )
            
            logger.info(f"HR Decision '{request.decision}' persisted for {target_cand.name}")
            
            return {
                "message": f"Decision '{request.decision}' recorded successfully.",
                "candidate_id": request.candidate_id,
                "hr_decision": {
                    "decision": request.decision,
                    "notes": request.notes,
                    "timestamp": datetime.now().isoformat(),
                    "status": "COMPLETED"
                }
            }
        finally:
            db.close()

    async def approve_interview(self, candidate_identifier: str) -> Dict[str, Any]:
        """
        Locks evaluation, validates state, and triggers the HITL Interview generation flow.
        """
        print(f"DEBUG: approve_interview called for {candidate_identifier}")
        db = SessionLocal()
        try:
            print(f"DEBUG: Starting DB query for {candidate_identifier}")
            cand = repository.get_candidate_by_fuzzy_id(db, candidate_identifier)
            if not cand:
                print(f"DEBUG: Candidate not found")
                raise ValueError(f"Candidate not found: {candidate_identifier}")
                
            print(f"DEBUG: Getting screening result for cand_id {cand.id}")
            screening = repository.get_latest_screening_result(db, cand.id)
            if not screening:
                print(f"DEBUG: No evaluation found")
                raise ValueError("No unified evaluation found to lock")

            print(f"DEBUG: Found screening. Locking...")
            # 1. Lock evaluation & update status
            screening.evaluation_locked = True
            screening.interview_status = "APPROVED"
            
            # 2. Trigger Session Creation (To be implemented in session_manager.py)
            from core.interview.session_manager import create_interview_session
            session_meta = create_interview_session(db, cand.id, screening.id)
            screening.interview_session_id = session_meta['session_id']

            # 3. Trigger Email (To be implemented in interview_email.py)
            from core.notifications.interview_email import send_interview_invite
            invite_sent = send_interview_invite(cand.email, session_meta['link'], cand.name)
            if invite_sent:
                screening.interview_invite_sent = True
                screening.interview_status = "INTERVIEW_SENT"

            db.commit()
            
            return {
                "message": "Candidate approved. Interview session created and invitation sent.",
                "candidate_id": candidate_identifier,
                "interview_status": screening.interview_status,
                "evaluation_locked": screening.evaluation_locked,
                "session_id": screening.interview_session_id
            }
        finally:
            db.close()

    async def run_stage_3_stream(self):
        """Unified Evaluation: Interview Readiness & Skeptic Agent for top 30."""
        from app.db.database import SessionLocal
        from app.db import repository
        import json

        db = SessionLocal()
        try:
            logger.info("[STAGE 3] Starting Unified Evaluation for Top 30 candidates")
            
            # 1. Get current results to identify candidates
            results = await self.get_stored_results()
            top_30_candidates = results.get("ranking", [])[:30]
            
            if not top_30_candidates:
                yield json.dumps({"error": "No candidates found to evaluate in Stage 3."}) + "\n"
                return

            # 2. Initialize Agents
            readiness_agent = Stage3ReadinessAgent()
            skeptic_agent = Stage3SkepticAgent()
            
            active_jd = await self._get_or_create_active_jd(db)
            jd_text = active_jd.jd_text

            yield json.dumps({
                "step": 1,
                "status": f"Stage 3: Starting analysis for Top {len(top_30_candidates)} candidates",
            }) + "\n"

            # 3. Process in batches (e.g., 5 at a time)
            batch_size = 5
            for i in range(0, len(top_30_candidates), batch_size):
                batch = top_30_candidates[i : i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(top_30_candidates) + batch_size - 1) // batch_size

                yield json.dumps({
                    "step": 2,
                    "status": f"Stage 3: Batch {batch_num}/{total_batches} — Running Readiness & Skeptic Audit",
                }) + "\n"

                tasks = []
                for cand_summary in batch:
                    cand_id = cand_summary["candidate_id"]
                    cand_name = cand_summary["name"]
                    eval_data = results["evaluations"].get(cand_id, {})
                    
                    # Readiness task
                    tasks.append(readiness_agent.evaluate_async(
                        cand_id, cand_name, jd_text, eval_data, eval_data
                    ))
                    # Skeptic task
                    tasks.append(skeptic_agent.evaluate_async(
                        cand_id, cand_name, jd_text, eval_data, eval_data
                    ))

                # Wait for batch to complete
                agent_results = await asyncio.gather(*tasks)

                # Each candidate has 2 results (Readiness, Skeptic)
                partial_evaluations = {}
                for idx, cand_summary in enumerate(batch):
                    cand_id = cand_summary["candidate_id"]
                    readiness_res = agent_results[idx * 2]
                    skeptic_res = agent_results[idx * 2 + 1]

                    # Store in DB
                    db_cand = repository.get_candidate_by_fuzzy_id(db, cand_id)
                    if db_cand:
                        res_rec = repository.get_latest_screening_result(db, db_cand.id)
                        if res_rec:
                            res_rec.interview_readiness_json = json.dumps(readiness_res)
                            res_rec.skeptic_analysis_json = json.dumps(skeptic_res)
                            db.commit()

                    # Deep merge with existing data to prevent UI data loss
                    cand_eval = results["evaluations"].get(cand_id, {}).copy()
                    cand_eval.update({
                        "interview_readiness": readiness_res,
                        "skeptic_analysis": skeptic_res
                    })
                    partial_evaluations[cand_id] = cand_eval

                yield json.dumps({
                    "step": 3,
                    "partial_results": {"evaluations": partial_evaluations},
                }) + "\n"

            yield json.dumps({
                "step": 4,
                "status": "Stage 3: Unified Evaluation Complete",
            }) + "\n"

        except Exception as e:
            logger.error(f"[STAGE 3] Pipeline Error: {e}")
            import traceback
            traceback.print_exc()
            yield json.dumps({"error": str(e)}) + "\n"
        finally:
            db.close()

pipeline_service = PipelineService()
