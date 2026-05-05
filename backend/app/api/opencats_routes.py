from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.database import get_db
from app.services.opencats_service import opencats_service

router = APIRouter()

@router.get("/candidates")
async def list_opencats_candidates(limit: int = 500, db: Session = Depends(get_db)):
    """
    List candidates from the OpenCATS database.
    """
    try:
        candidates = opencats_service.list_candidates(db, limit=limit)
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candidates/{candidate_id}/analysis")
async def analyze_opencats_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """
    Trigger AI analysis for a specific OpenCATS candidate.
    """
    try:
        analysis = await opencats_service.analyze_candidate(db, candidate_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/candidates/{candidate_id}/analyze-upload")
async def analyze_candidate_upload(candidate_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Analyze an uploaded resume file for a specific OpenCATS candidate.
    """
    try:
        content = await file.read()
        analysis = await opencats_service.analyze_candidate_file(db, candidate_id, content, file.filename)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
