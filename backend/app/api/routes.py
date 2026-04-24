import os
from fastapi import APIRouter, HTTPException, Depends, Body, File, UploadFile
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from app.models.response_models import ScreeningResponse, HRDecisionRequest
from app.services.pipeline_service import pipeline_service
from app.services.interview_service import interview_service
from app.services.report_service import report_service
from app.db.database import get_db
from app.db import repository

router = APIRouter()

@router.get("/health")
async def health_check():
    print("====== FRONTEND CONNECTED: Health check ping received! ======")
    return {"status": "running"}


@router.get("/sql-audit/results")
async def get_sql_audit_results():
    """
    Returns the processed SQL test results from Neon DB.
    """
    try:
        results = repository.get_sql_test_results()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(days: int = 30, job_status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns real-time recruitment metrics from the production database.
    """
    try:
        stats = repository.get_recruitment_stats(db, days=days, job_status=job_status)
        return stats
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/funnel")
async def get_funnel(days: int = 30, joborder_id: Optional[int] = None, recruiter_id: Optional[int] = None, job_status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns recruitment funnel analytics with filtering support.
    """
    try:
        funnel_data = repository.get_funnel_stats(db, days=days, job_id=joborder_id, recruiter_id=recruiter_id, job_status=job_status)
        return funnel_data
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch funnel stats: {str(e)}")

@router.get("/jobs")
async def get_jobs(db: Session = Depends(get_db)):
    """Returns all active job orders for filtering."""
    try:
        return repository.get_jobs(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recruiters")
async def get_recruiters(db: Session = Depends(get_db)):
    """Returns all recruiters for filtering."""
    try:
        return repository.get_recruiters(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/placements/active")
async def get_active_placements_api(db: Session = Depends(get_db)):
    """
    Returns a list of candidates currently in the 'Interviewing' stage.
    """
    try:
        placements = repository.get_active_placements(db)
        return placements
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch active placements: {str(e)}")

class ScreeningRequest(BaseModel):
    evaluation_weights: Optional[Dict[str, float]] = None

@router.post("/screen", response_model=ScreeningResponse)
async def run_screening(req: ScreeningRequest = Body(default=None)):
    try:
        weights = req.evaluation_weights if req else None
        results = await pipeline_service.run_screening(evaluation_weights=weights)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline screening failed: {str(e)}")

@router.get("/results", response_model=ScreeningResponse)
async def get_results():
    try:
        results = await pipeline_service.get_stored_results()
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")

@router.post("/re-evaluate/{candidate_id}")
async def re_evaluate_candidate(candidate_id: str):
    try:
        results = await pipeline_service.re_evaluate(candidate_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Re-evaluation failed: {str(e)}")

@router.post("/candidate/{candidate_id}/approve-interview")
async def approve_interview(candidate_id: str):
    try:
        result = await pipeline_service.approve_interview(candidate_id)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to approve interview: {str(e)}")

class ForceEvaluateRequest(BaseModel):
    evaluation_weights: Optional[Dict[str, float]] = None

@router.post("/force-evaluate/{candidate_id}")
async def force_evaluate_candidate(candidate_id: str, req: ForceEvaluateRequest = Body(default=None)):
    try:
        weights = req.evaluation_weights if req else None
        results = await pipeline_service.force_evaluate(candidate_id, evaluation_weights=weights)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Force evaluation failed: {str(e)}")

@router.post("/screen-stream")
async def run_screening_stream(req: ScreeningRequest = Body(default=None)):
    from fastapi.responses import StreamingResponse
    try:
        weights = req.evaluation_weights if req else None
        return StreamingResponse(
            pipeline_service.run_screening_stream(evaluation_weights=weights),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming Pipeline failed: {str(e)}")

@router.post("/run-stage-2-stream")
async def run_stage_2_stream():
    from fastapi.responses import StreamingResponse
    try:
        return StreamingResponse(
            pipeline_service.run_stage_2_stream(),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stage 2 Pipeline failed: {str(e)}")

@router.post("/run-stage-3-stream")
async def run_stage_3_stream():
    from fastapi.responses import StreamingResponse
    try:
        return StreamingResponse(
            pipeline_service.run_stage_3_stream(),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stage 3 Pipeline failed: {str(e)}")

@router.post("/hr-decision")
async def submit_hr_decision(request: HRDecisionRequest):
    try:
        return await pipeline_service.submit_hr_decision(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit HR decision: {str(e)}")

@router.get("/rag/metrics/{candidate_id}")
async def get_rag_metrics(candidate_id: str):
    try:
        return await pipeline_service.get_candidate_rag_metrics(candidate_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/rag-override/{candidate_id}")
async def toggle_rag_override(candidate_id: str, payload: Dict[str, bool] = Body(...)):
    try:
        override = payload.get("override", False)
        return await pipeline_service.toggle_rag_override(candidate_id, override)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag/summary")
async def get_rag_summary():
    try:
        return await pipeline_service.get_rag_run_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag/retrieval-metrics/{candidate_id}")
async def get_rag_retrieval_metrics_api(candidate_id: str, db: Session = Depends(get_db)):
    try:
        from app.db import repository

        db_cand = repository.get_candidate_by_fuzzy_id(db, candidate_id)
        if not db_cand:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        metrics = repository.get_rag_retrieval_metrics(db, db_cand.id)
        if not metrics:
            return None

        return {
            "precision": metrics.precision,
            "recall": metrics.recall,
            "coverage": metrics.coverage,
            "similarity": metrics.similarity,
            "diversity": metrics.diversity,
            "density": metrics.density,
            "overall_score": metrics.overall_score,
            "rag_health_status": metrics.rag_health_status,
            "evaluated_at": metrics.evaluated_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Interview Intelligence Routes ---

@router.post("/interview/start")
async def start_interview(candidate_id: int, job_id: int):
    try:
        return await interview_service.start_interview(candidate_id, job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interview/{session_id}/state")
async def get_interview_state(session_id: str):
    try:
        return await interview_service.get_interview_state(session_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/interview/{session_id}/answer")
async def submit_answer(session_id: str, payload: Dict[str, str] = Body(...)):
    try:
        answer = payload.get("answer")
        if not answer:
            raise HTTPException(status_code=400, detail="Answer is required")
        return await interview_service.submit_answer(session_id, answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/candidates/upload")
async def upload_candidates(file: UploadFile = File(...)):
    """
    Uploads a CSV/Excel file of candidates and returns a preview.
    """
    import shutil
    import tempfile
    
    # Save uploaded file to temp
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    try:
        from app.services.data_ingestion import data_ingestion_service
        candidates = data_ingestion_service.parse_file(tmp_path)
        return {"filename": file.filename, "count": len(candidates), "candidates": candidates[:10]} # Preview first 10
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/candidates/upload-screen")
async def upload_and_screen(file: UploadFile = File(...), req: Optional[Dict[str, Any]] = Body(None)):
    """
    Uploads a file and immediately runs the screening pipeline.
    """
    import shutil
    import tempfile
    
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
        
    try:
        weights = req.get("evaluation_weights") if req else None
        results = await pipeline_service.run_bulk_screening(tmp_path, evaluation_weights=weights)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk screening failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.get("/candidate/{candidate_id}/report-html")
async def get_candidate_report_html(candidate_id: str):
    """
    Returns a self-contained HTML report for a candidate.
    """
    try:
        results = await pipeline_service.get_stored_results()
        eval_data = results.get("evaluations", {}).get(candidate_id)
        if not eval_data:
            # Try fuzzy match if exact match fails
            for cid in results.get("evaluations", {}):
                if candidate_id.lower() in cid.lower():
                    eval_data = results["evaluations"][cid]
                    candidate_id = cid
                    break
                    
        if not eval_data:
            raise HTTPException(status_code=404, detail=f"Report data for candidate {candidate_id} not found.")

        # Find basic info from ranking
        cand_basic = next((c for c in results.get("ranking", []) if c["candidate_id"] == candidate_id), {})
        
        from fastapi.responses import HTMLResponse
        report_html = report_service.generate_candidate_report(cand_basic, eval_data)
        headers = {
            "Content-Disposition": f"attachment; filename=Report_{candidate_id}.html"
        }

        return HTMLResponse(content=report_html, headers=headers)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
