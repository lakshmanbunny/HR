from sqlalchemy.orm import Session
from . import models
from .models import Candidate, JobDescription, ScreeningResult, InterviewSession, RAGMetric
import json
from typing import List, Optional, Dict

# --- Candidate Repositories ---
def create_candidate(db: Session, name: str, email: str, github_url: str, linkedin_url: Optional[str] = None):
    db_candidate = Candidate(
        name=name,
        email=email,
        github_url=github_url,
        linkedin_url=linkedin_url
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def get_candidate(db: Session, candidate_id: int):
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()

def get_candidate_by_email(db: Session, email: str):
    return db.query(Candidate).filter(Candidate.email == email).first()

def get_candidate_by_fuzzy_id(db: Session, identifier: str):
    """
    Robustly finds a candidate by ID, full email, or roll number/email prefix.
    """
    if not identifier:
        return None
        
    identifier_str = str(identifier).strip()
    
    # 1. Try by Integer ID
    if identifier_str.isdigit():
        cand = get_candidate(db, int(identifier_str))
        if cand: return cand
        
    # 2. Try by Full Email
    cand = get_candidate_by_email(db, identifier_str.lower())
    if cand: return cand
    
    # 3. Try by Email Prefix (Roll Number)
    # Most candidates in our DB have email as roll_number@domain.com
    prefix = identifier_str.split('@')[0].lower()
    cand = db.query(Candidate).filter(Candidate.email.like(f"{prefix}%")).first()
    if cand: return cand
    
    # 4. Try by Woxsen Roll Number
    from .models import WoxsenCandidate
    wc = db.query(WoxsenCandidate).filter(WoxsenCandidate.roll_number.ilike(identifier_str)).first()
    if not wc:
        # Try partial roll number match
        wc = db.query(WoxsenCandidate).filter(WoxsenCandidate.roll_number.ilike(f"%{identifier_str}%")).first()
    
    if wc:
        cand = get_candidate_by_email(db, wc.email)
        if cand: return cand
    
    # 5. Try by Name Case-Insensitive (Fallback)
    cand = db.query(Candidate).filter(Candidate.name.ilike(f"%{identifier_str}%")).first()
    
    return cand

def list_candidates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Candidate).offset(skip).limit(limit).all()

def list_woxsen_candidates(db: Session):
    return db.query(models.WoxsenCandidate).all()

# --- JD Repositories ---
def create_job_description(db: Session, jd_text: str):
    jd_hash = JobDescription.generate_hash(jd_text)
    # Check if exists
    existing = get_jd_by_hash(db, jd_hash)
    if existing:
        return existing
        
    db_jd = JobDescription(
        jd_text=jd_text,
        jd_hash=jd_hash,
        is_active=True
    )
    # Mark others as inactive if needed, or handle active JD logic separately
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

def get_active_jd(db: Session):
    return db.query(JobDescription).filter(JobDescription.is_active == True).order_by(JobDescription.created_at.desc()).first()

def get_jd_by_hash(db: Session, jd_hash: str):
    return db.query(JobDescription).filter(JobDescription.jd_hash == jd_hash).first()

def get_job_description(db: Session, job_id: int):
    return db.query(JobDescription).filter(JobDescription.id == job_id).first()

# --- Screening Results Repositories ---
def get_screening_result(db: Session, candidate_id: int, jd_id: int):
    return db.query(ScreeningResult).filter(
        ScreeningResult.candidate_id == candidate_id,
        ScreeningResult.jd_id == jd_id
    ).first()

def get_latest_screening_result(db: Session, candidate_id: int):
    return db.query(ScreeningResult).filter(ScreeningResult.candidate_id == candidate_id).order_by(ScreeningResult.evaluated_at.desc()).first()

def list_screening_results(db: Session, jd_id: int):
    return db.query(ScreeningResult).filter(ScreeningResult.jd_id == jd_id).all()

def save_screening_result(db: Session, candidate_id: int, jd_id: int, result_data: dict):
    # Check if exists to update or create
    existing = get_screening_result(db, candidate_id, jd_id)
    
    # Preserve HR decisions if they exist
    hr_decision = None
    hr_notes = None
    if existing:
        hr_decision = existing.hr_decision
        hr_notes = existing.hr_notes
        db.delete(existing)
        db.commit()

    db_result = ScreeningResult(
        candidate_id=candidate_id,
        jd_id=jd_id,
        resume_score=result_data.get("resume_score"),
        github_score=result_data.get("github_score"),
        overall_score=result_data.get("overall_score"),
        risk_level=result_data.get("risk_level"),
        readiness_level=result_data.get("readiness_level"),
        recommendation=result_data.get("recommendation"),
        repo_count=result_data.get("repo_count", 0),
        ai_projects=result_data.get("ai_projects", 0),
        skill_gaps_json=json.dumps(result_data.get("skill_gaps", [])),
        interview_focus_json=json.dumps(result_data.get("interview_focus", [])),
        github_features_json=json.dumps(result_data.get("github_features", [])),
        repos_json=json.dumps(result_data.get("repos", [])),
        interview_readiness_json=json.dumps(result_data.get("interview_readiness", {})),
        skeptic_analysis_json=json.dumps(result_data.get("skeptic_analysis", {})),
        final_synthesized_decision_json=json.dumps(result_data.get("final_synthesized_decision", {})),
        ai_evidence_json=json.dumps(result_data.get("ai_evidence", [])),
        justification_json=json.dumps(result_data.get("justification", [])),
        judge_audit_json=json.dumps(result_data.get("judge_audit", {})),
        rubric_scores_json=json.dumps(result_data.get("rubric_scores", {})),
        rank_position=result_data.get("rank_position"),
        
        # New RAG Metadata
        retrieval_mode=result_data.get("retrieval_mode", "agent_pipeline"),
        retrieval_version=result_data.get("retrieval_version"),
        rag_enabled=result_data.get("rag_enabled", True),
        rag_status=result_data.get("rag_status", "healthy"),

        hr_decision=hr_decision,
        hr_notes=hr_notes
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def clear_stale_results(db: Session, current_version: str):
    """Deletes all screening results that don't match the current retrieval version."""
    stale = db.query(ScreeningResult).filter(ScreeningResult.retrieval_version != current_version).all()
    if stale:
        for result in stale:
            db.delete(result)
        db.commit()
        return len(stale)
    return 0

def update_screening_hr_decision(db: Session, candidate_id: int, jd_id: int, decision: str, notes: Optional[str] = None):
    db_result = get_screening_result(db, candidate_id, jd_id)
    if db_result:
        db_result.hr_decision = decision
        if notes is not None:
            db_result.hr_notes = notes
        db.commit()
        db.refresh(db_result)
    return db_result

def delete_screening_result(db: Session, candidate_id: int, jd_id: int):
    result = get_screening_result(db, candidate_id, jd_id)
    if result:
        db.delete(result)
        db.commit()
        return True
    return False

def update_screening_audit(db: Session, candidate_id: int, jd_id: int, agent_type: str, audit_data: dict):
    """
    Updates the audit results for a specific agent type in the ScreeningResult record.
    agent_type can be 'unified', 'readiness', or 'skeptic'.
    """
    result = get_screening_result(db, candidate_id, jd_id)
    if not result:
        return None
        
    if agent_type == 'unified':
        result.judge_audit_json = json.dumps(audit_data)
    elif agent_type == 'readiness':
        data = json.loads(result.interview_readiness_json or "{}")
        data["judge_audit"] = audit_data
        result.interview_readiness_json = json.dumps(data)
    elif agent_type == 'skeptic':
        data = json.loads(result.skeptic_analysis_json or "{}")
        data["judge_audit"] = audit_data
        result.skeptic_analysis_json = json.dumps(data)
        
    db.commit()
    db.refresh(result)
    return result

# --- Interview Session Repositories ---
def create_interview_session(db: Session, candidate_id: int, session_id: str, job_id: Optional[int] = None):
    db_session = InterviewSession(
        candidate_id=candidate_id,
        session_id=session_id,
        job_id=job_id,
        status="pending",
        questions_json=json.dumps([]),
        answers_json=json.dumps([]),
        followups_json=json.dumps([]),
        transcript_summary="",
        final_scores_json=json.dumps({}),
        current_question_index=0
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_interview_session(db: Session, session_id: str):
    return db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()

def get_active_interview_session_by_candidate(db: Session, candidate_id: int):
    return db.query(InterviewSession).filter(
        InterviewSession.candidate_id == candidate_id,
        InterviewSession.status != "completed"
    ).order_by(InterviewSession.created_at.desc()).first()

def update_interview_progress(db: Session, session_id: str, progress_data: dict):
    db_session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if db_session:
        if "questions" in progress_data:
            db_session.questions_json = json.dumps(progress_data["questions"])
        if "answers" in progress_data:
            db_session.answers_json = json.dumps(progress_data["answers"])
        if "followups" in progress_data:
            db_session.followups_json = json.dumps(progress_data["followups"])
        if "summary" in progress_data:
            db_session.transcript_summary = progress_data["summary"]
        if "scores" in progress_data:
            db_session.final_scores_json = json.dumps(progress_data["scores"])
        if "current_index" in progress_data:
            db_session.current_question_index = progress_data["current_index"]
        if "status" in progress_data:
            db_session.status = progress_data["status"]
            
        db.commit()
        db.refresh(db_session)
    return db_session

def finalize_interview_session(db: Session, session_id: str, final_data: dict):
    db_session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if db_session:
        db_session.status = "completed"
        db_session.interview_score = final_data.get("overall_score")
        db_session.final_scores_json = json.dumps(final_data.get("scores", {}))
        db_session.recommendation = final_data.get("recommendation")
        db_session.completed_at = func.now()
        db.commit()
        db.refresh(db_session)
    return db_session

def save_rag_metrics(db: Session, candidate_id: int, screening_result_id: int, metrics: dict):
    """Saves RAG evaluation metrics for a screening run."""
    db_metrics = RAGMetric(
        candidate_id=candidate_id,
        screening_result_id=screening_result_id,
        retrieval_score=metrics.get("retrieval_score", 0.0),
        faithfulness_score=metrics.get("faithfulness_score", 0.0),
        coverage_score=metrics.get("coverage_score", 0.0),
        precision_score=metrics.get("precision_score", 0.0),
        recall_score=metrics.get("recall_score", metrics.get("recall", 0.0)),
        relevancy_score=metrics.get("relevancy_score", metrics.get("answer_relevancy", 0.0)),
        rag_health_status=metrics.get("rag_health_status", "CRITICAL")
    )
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

def get_rag_metrics(db: Session, candidate_id: int):
    """Retrieves the latest RAG metrics for a candidate."""
    return db.query(RAGMetric).filter(RAGMetric.candidate_id == candidate_id)\
             .order_by(RAGMetric.evaluation_timestamp.desc()).first()

def update_rag_override(db: Session, screening_result_id: int, override_status: bool):
    """Updates the RAG override flag for a screening result."""
    result = db.query(ScreeningResult).filter(ScreeningResult.id == screening_result_id).first()
    if result:
        result.rag_override = override_status
        db.commit()
        db.refresh(result)
        return result
    return None


# --- RAGEvaluationResult Repositories ---

def get_rag_retrieval_metrics(db: Session, candidate_id: int):
    """Fetches the latest deterministic RAG retrieval metrics for a candidate."""
    from .models import RAGRetrievalMetric
    return db.query(RAGRetrievalMetric).filter(RAGRetrievalMetric.candidate_id == candidate_id).order_by(RAGRetrievalMetric.evaluated_at.desc()).first()

def list_all_rag_retrieval_metrics(db: Session):
    """Returns all RAGRetrievalMetric records joined to their Candidate, sorted by overall_score desc."""
    from .models import RAGRetrievalMetric
    return (
        db.query(RAGRetrievalMetric)
        .join(Candidate, RAGRetrievalMetric.candidate_id == Candidate.id)
        .order_by(RAGRetrievalMetric.overall_score.desc())
        .all()
    )

def save_rag_retrieval_metrics(db: Session, candidate_id: int, metrics: dict):
    """Persists deterministic zero-LLM retrieval metrics."""
    from .models import RAGRetrievalMetric
    
    # Remove older record to keep history clean/flat per candidate
    existing = db.query(RAGRetrievalMetric).filter(RAGRetrievalMetric.candidate_id == candidate_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        
    db_metrics = RAGRetrievalMetric(
        candidate_id=candidate_id,
        precision=metrics.get('precision', 0.0),
        recall=metrics.get('recall', 0.0),
        coverage=metrics.get('coverage', 0.0),
        similarity=metrics.get('similarity', 0.0),
        diversity=metrics.get('diversity', 0.0),
        density=metrics.get('density', 0.0),
        overall_score=metrics.get('overall_score', 0.0),
        rag_health_status=metrics.get('rag_health_status', 'CRITICAL')
    )
    
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics


def get_active_placements(db: Session):
    """
    Fetches details of candidates currently in the 'Interviewing' (500) stage.
    """
    from sqlalchemy import text
    query = text("""
        SELECT 
            c.first_name, c.last_name, j.title as job_title, 
            cjs.short_description as status,
            DATEDIFF(NOW(), cj.date_modified) as days_in_stage
        FROM candidate_joborder cj
        JOIN candidate c ON cj.candidate_id = c.candidate_id
        JOIN joborder j ON cj.joborder_id = j.joborder_id
        JOIN candidate_joborder_status cjs ON cj.status = cjs.candidate_joborder_status_id
        WHERE cj.status = 500
        ORDER BY days_in_stage DESC
        LIMIT 10
    """)
    res = db.execute(query).fetchall()
    return [{"name": f"{r[0]} {r[1]}", "job": r[2], "status": r[3], "days": r[4]} for r in res]

def get_recruitment_stats(db: Session, days: int = 30):
    """
    Fetches real-time recruitment metrics from the production database using direct SQL.
    Computes hiring velocity, onboarding ratios, and category performance with date filtering.
    """
    from sqlalchemy import text
    stats = {}
    
    # Date filter fragments
    date_filter_cand = f"WHERE date_created >= DATE_SUB(NOW(), INTERVAL {days} DAY)"
    date_filter_cj = f"WHERE date_modified >= DATE_SUB(NOW(), INTERVAL {days} DAY)"
    date_filter_cj_created = f"WHERE date_created >= DATE_SUB(NOW(), INTERVAL {days} DAY)"
    date_filter_job = f"WHERE date_created >= DATE_SUB(NOW(), INTERVAL {days} DAY)"
    
    # For large time ranges (e.g. 1000 days), we might want to skip filters to see total history
    if days > 999:
        date_filter_cand = ""
        date_filter_cj = ""
        date_filter_cj_created = ""
        date_filter_job = ""

    try:
        # 1. New Core Metrics requested by user
        # Total Active Openings (currently active AND created in the last N days)
        res = db.execute(text(f"SELECT COUNT(*) FROM joborder WHERE (status = 'Active' OR status = '100') {date_filter_job.replace('WHERE', 'AND') if date_filter_job else ''}")).fetchone()
        stats["total_active_openings"] = res[0] if res else 0
        
        # Enrolled/Considered Candidates for those active openings
        query_considered = text(f"""
            SELECT COUNT(DISTINCT cj.candidate_id) 
            FROM candidate_joborder cj 
            JOIN joborder j ON cj.joborder_id = j.joborder_id 
            WHERE (j.status = 'Active' OR j.status = '100')
            {date_filter_cj_created.replace('WHERE', 'AND cj.') if date_filter_cj_created else ''}
        """)
        res = db.execute(query_considered).fetchone()
        stats["total_considered_candidates"] = res[0] if res else 0

        # Legacy counts for backward compatibility/context
        res = db.execute(text(f"SELECT COUNT(*) FROM candidate {date_filter_cand}")).fetchone()
        total_candidates = res[0] if res else 0
        stats["total_candidates"] = total_candidates
        
        res = db.execute(text(f"SELECT COUNT(*) FROM joborder {date_filter_job}")).fetchone()
        stats["total_jobs"] = res[0] if res else 0
        
        res = db.execute(text(f"SELECT COUNT(*) FROM company")).fetchone() # Companies usually don't have a date filter needed here
        stats["total_companies"] = res[0] if res else 0
        
        # 2. Sourcing Mix (Top 5)
        res = db.execute(text(f"""
            SELECT COALESCE(NULLIF(source, ''), 'Other/Direct') as source, COUNT(*) as count 
            FROM candidate 
            {date_filter_cand}
            GROUP BY source 
            ORDER BY count DESC 
            LIMIT 5
        """)).fetchall()
        stats["sourcing_mix"] = [{"source": r[0], "count": r[1]} for r in res]
        
        # 3. Deep Metrics: Time to Fill (Status 800 = Placed)
        res = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder WHERE status = 800 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()
        stats["avg_time_to_fill"] = round(res[0], 1) if res and res[0] is not None else 0
        
        # 3b. Average Time to Offer (Status 600 = Offered)
        res_offer = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder WHERE status = 600 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()
        stats["avg_time_to_offer"] = round(res_offer[0], 1) if res_offer and res_offer[0] is not None else 0
        
        # 4. Deep Metrics: Onboarding Ratio (Placed / Total * 100)
        res = db.execute(text(f"SELECT COUNT(*) FROM candidate_joborder WHERE status = 800 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()
        placed_count = res[0] if res else 0
        stats["onboarding_ratio"] = round((placed_count / total_candidates * 100), 1) if total_candidates > 0 else 0
        
        # 5. Pipeline Conversion: Interview to Placement
        res = db.execute(text(f"SELECT COUNT(*) FROM candidate_joborder WHERE status = 500 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()
        interviewed_count = res[0] if res else 0
        stats["pipeline_conversion"] = round((placed_count / interviewed_count * 100), 1) if interviewed_count > 0 else 0
        stats["interviewed_count"] = interviewed_count

        # 6. Dynamic Category Performance (Funnel Success Rate per Job Title)
        query_categories = text(f"""
            SELECT 
                j.title, 
                COUNT(cj.candidate_id) as total,
                SUM(CASE WHEN cj.status = 800 THEN 1 ELSE 0 END) as success
            FROM joborder j
            JOIN candidate_joborder cj ON j.joborder_id = cj.joborder_id
            WHERE 1=1 {date_filter_cj_created.replace('WHERE', 'AND cj.') if date_filter_cj_created else ''}
            GROUP BY j.title
            ORDER BY total DESC
            LIMIT 8
        """)
        
        cat_res = db.execute(query_categories).fetchall()
        stats["category_performance"] = [
            {
                "label": r[0], 
                "success": round((r[2] / r[1] * 100), 1) if r[1] > 0 else 0,
                "total": r[1]
            } for r in cat_res
        ]

        # 7. Velocity Stages
        res_s = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder WHERE status = 400 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()
        res_i = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder WHERE status = 500 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()
        res_p = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder WHERE status = 800 {date_filter_cj.replace('WHERE', 'AND') if date_filter_cj else ''}")).fetchone()

        stats["velocity_stages"] = [
            {"stage": "Initial Screening", "days": round(res_s[0], 1) if res_s and res_s[0] is not None else 1.0},
            {"stage": "Client Interviewing", "days": round(res_i[0], 1) if res_i and res_i[0] is not None else 3.6},
            {"stage": "Final Placement", "days": round(res_p[0], 1) if res_p and res_p[0] is not None else 30.3}
        ]
        
    except Exception as e:
        import traceback
        print(f"CRITICAL: Error fetching recruitment stats: {e}")
        traceback.print_exc()
        # Ensure we return at least what we have, or zeros if it failed early
        if not stats:
            stats = {
                "total_candidates": 0, "total_jobs": 0, "total_companies": 0, "total_active_openings": 0,
                "total_considered_candidates": 0, "active_jobs": 0, "onboarding_ratio": 0, 
                "avg_time_to_fill": 0, "avg_time_to_offer": 0, "pipeline_conversion": 0, "sourcing_mix": [], 
                "velocity_stages": [], "category_performance": [{"label": "N/A", "success": 0}]
            }
    return stats
    return stats

def get_funnel_stats(db: Session, days: int = 30, job_id: Optional[int] = None, recruiter_id: Optional[int] = None):
    """
    Calculates recruitment funnel stages with propagation logic.
    Stages: Submissions, Pre-screening, Written, L1, L2, L3, Offered, Joined.
    """
    from sqlalchemy import text
    import re

    # 1. Base Query for Candidate-Job pairs
    where_clauses = ["cj.status >= 100"] 
    params = {"days": days}
    
    if days <= 999:
        where_clauses.append("cj.date_created >= DATE_SUB(NOW(), INTERVAL :days DAY)")
    
    if job_id:
        where_clauses.append("cj.joborder_id = :job_id")
        params["job_id"] = job_id
        
    if recruiter_id:
        where_clauses.append("j.recruiter = :recruiter_id")
        params["recruiter_id"] = recruiter_id

    where_str = " AND ".join(where_clauses)
    
    query = text(f"""
        SELECT 
            cj.candidate_id, 
            cj.joborder_id, 
            cj.status
        FROM candidate_joborder cj
        JOIN joborder j ON cj.joborder_id = j.joborder_id
        WHERE {where_str}
    """)
    
    rows = db.execute(query, params).fetchall()
    
    if not rows:
        return []

    # 2. Activity Query for granular stages
    job_ids = list(set([r[1] for r in rows]))
    activity_query = text(f"""
        SELECT joborder_id, data_item_id as candidate_id, notes 
        FROM activity 
        WHERE data_item_type = 100 
        AND joborder_id IN ({','.join(map(str, job_ids))})
    """)
    activities = db.execute(activity_query).fetchall()
    
    activity_map = {}
    job_has_stages = {} 
    
    for act_job_id, cand_id, notes in activities:
        key = (cand_id, act_job_id)
        if key not in activity_map: activity_map[key] = []
        activity_map[key].append(str(notes or "").lower())
        
        if act_job_id not in job_has_stages: 
            job_has_stages[act_job_id] = {"L2": False, "L3": False, "Written": False}
        
        n = str(notes or "").lower()
        if "l2" in n: job_has_stages[act_job_id]["L2"] = True
        if "l3" in n: job_has_stages[act_job_id]["L3"] = True
        if "written" in n: job_has_stages[act_job_id]["Written"] = True

    counts = {
        "Submissions": 0, "Pre-screening": 0, "Written": 0,
        "L1 interview": 0, "L2 interview": 0, "L3 interview": 0,
        "Offered": 0, "Joined": 0
    }
    
    for cand_id, j_id, status in rows:
        key = (cand_id, j_id)
        cand_activities = activity_map.get(key, [])
        j_stages = job_has_stages.get(j_id, {"L2": False, "L3": False, "Written": False})
        
        reached = {"Sub": False, "Pre": False, "Writ": False, "L1": False, "L2": False, "L3": False, "Off": False, "Join": False}
        
        # New Strict Mapping Logic:
        # Success Chain: 100 (No Contact) -> 300/400 (Screening/Sub) -> 500 (Int) -> 600 (Off) -> 800 (Join)
        if status == 800:
            reached["Join"] = True
            reached["Off"] = True
            reached["L1"] = True
            reached["L2"] = True
            reached["L3"] = True
            reached["Writ"] = True
            reached["Pre"] = True
            reached["Sub"] = True
        elif status == 600:
            reached["Off"] = True
            reached["L1"] = True
            reached["L2"] = True
            reached["L3"] = True
            reached["Writ"] = True
            reached["Pre"] = True
            reached["Sub"] = True
        elif status == 500:
            reached["L1"] = True
            reached["Pre"] = True
            reached["Sub"] = True
        elif status >= 300: # Includes 300 and 400
            reached["Pre"] = True
            reached["Sub"] = True
        elif status >= 100:
            reached["Sub"] = True

        # Activity-based propagation (Wait for notes like L2/L3)
        if status == 500:
            is_l2 = any("l2" in a for a in cand_activities)
            is_l3 = any("l3" in a for a in cand_activities)
            if is_l3: reached["L3"] = True
            if is_l2 or is_l3: reached["L2"] = True
            
            # If the job itself doesn't have these stages, propagate them to fill the funnel
            if not j_stages["L2"] and reached["L1"]: reached["L2"] = True
            if not j_stages["L3"] and reached["L2"]: reached["L3"] = True
            
        if reached["Writ"] or any("written" in a for a in cand_activities):
            reached["Writ"] = True
        elif not j_stages["Written"] and reached["Pre"]:
            reached["Writ"] = True 

        # Final cleanup for Join/Off consistency
        if reached["Join"] or reached["Off"]:
            reached["Sub"] = reached["Pre"] = reached["Writ"] = reached["L1"] = reached["L2"] = reached["L3"] = True
        if reached["Sub"]: counts["Submissions"] += 1
        if reached["Pre"]: counts["Pre-screening"] += 1
        if reached["Writ"]: counts["Written"] += 1
        if reached["L1"]: counts["L1 interview"] += 1
        if reached["L2"]: counts["L2 interview"] += 1
        if reached["L3"]: counts["L3 interview"] += 1
        if reached["Off"]: counts["Offered"] += 1
        if reached["Join"]: counts["Joined"] += 1

    return [
        {"stage": "Submissions", "count": counts["Submissions"]},
        {"stage": "Pre-screening", "count": counts["Pre-screening"]},
        {"stage": "Written", "count": counts["Written"]},
        {"stage": "L1 interview", "count": counts["L1 interview"]},
        {"stage": "L2 interview", "count": counts["L2 interview"]},
        {"stage": "L3 interview", "count": counts["L3 interview"]},
        {"stage": "Offered", "count": counts["Offered"]},
        {"stage": "Joined", "count": counts["Joined"]},
    ]

def get_job_time_metrics(db: Session, job_id: Optional[int] = None):
    """
    Calculates average time-to-offer and time-to-fill for a specific job order (or overall).
    Returns stage-by-stage velocity for granular forecasting.
    """
    from sqlalchemy import text
    
    job_filter = f"AND cj.joborder_id = {job_id}" if job_id else ""
    
    try:
        # Avg time to Screening (status 400)
        res_s = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder cj WHERE cj.status = 400 {job_filter}")).fetchone()
        # Avg time to Interview (status 500)
        res_i = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder cj WHERE cj.status = 500 {job_filter}")).fetchone()
        # Avg time to Offer (status 600)
        res_o = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder cj WHERE cj.status = 600 {job_filter}")).fetchone()
        # Avg time to Placement/Joined (status 800)
        res_p = db.execute(text(f"SELECT AVG(DATEDIFF(date_modified, date_created)) FROM candidate_joborder cj WHERE cj.status = 800 {job_filter}")).fetchone()
        # Total placements count for this job
        res_count = db.execute(text(f"SELECT COUNT(*) FROM candidate_joborder cj WHERE cj.status = 800 {job_filter}")).fetchone()
        
        def safe_float(val):
            """Convert Decimal/None to float for JSON serialization."""
            return float(round(val, 1)) if val is not None else None
        
        return {
            "avg_time_to_screening_days": safe_float(res_s[0]) if res_s else None,
            "avg_time_to_interview_days": safe_float(res_i[0]) if res_i else None,
            "avg_time_to_offer_days": safe_float(res_o[0]) if res_o else None,
            "avg_time_to_fill_days": safe_float(res_p[0]) if res_p else None,
            "total_placements": int(res_count[0]) if res_count else 0,
            "job_id": job_id
        }
    except Exception as e:
        return {
            "avg_time_to_screening_days": None,
            "avg_time_to_interview_days": None,
            "avg_time_to_offer_days": None,
            "avg_time_to_fill_days": None,
            "total_placements": 0,
            "job_id": job_id
        }

def get_jobs(db: Session):
    """Fetches all active job orders."""
    from sqlalchemy import text
    query = text("SELECT joborder_id, title FROM joborder WHERE status = 'Active' OR status = '100'")
    res = db.execute(query).fetchall()
    return [{"id": r[0], "title": r[1]} for r in res]

def get_recruiters(db: Session):
    """Fetches all users who are recruiters or owners of job orders."""
    from sqlalchemy import text
    query = text("""
        SELECT DISTINCT u.user_id, u.first_name, u.last_name 
        FROM user u 
        JOIN joborder j ON u.user_id = j.recruiter
        WHERE u.access_level >= 100
    """)
    res = db.execute(query).fetchall()
    return [{"id": r[0], "name": f"{r[1]} {r[2]}"} for r in res]

def get_sql_test_results():
    """
    Fetches processed SQL test results from the Neon PostgreSQL database.
    Note: This uses a separate engine/connection from the main MySQL DB.
    """
    import os
    from sqlalchemy import create_engine, text
    NEON_URL = "postgresql://neondb_owner:npg_5TvfU4MYdyxC@ep-wild-art-amr6ah4r-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    
    try:
        engine = create_engine(NEON_URL)
        with engine.connect() as conn:
            query = text("SELECT id, candidate_id, candidate_name, test_json, summary_score, weakest_topics, pdf_filename, processed_at FROM sql_test_results ORDER BY processed_at DESC")
            res = conn.execute(query).fetchall()
            
            results = []
            for r in res:
                results.append({
                    "id": r[0],
                    "candidate_id": r[1],
                    "candidate_name": r[2],
                    "questions": r[3], # JSONB field
                    "score": r[4],
                    "weakest_topics": r[5],
                    "filename": r[6],
                    "processed_at": r[7].isoformat() if r[7] else None
                })
            return results
    except Exception as e:
        return []
