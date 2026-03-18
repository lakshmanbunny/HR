import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime

# Set paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
DB_PATH = os.path.join(BACKEND_DIR, "paradigm_ai.db")

def format_list(data, header=""):
    if not data:
        return ""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return data
    if isinstance(data, list):
        items = [f"• {item}" for item in data if item]
        if not items:
            return ""
        result = "\n".join(items)
        if header:
            return f"\n【{header}】\n{result}"
        return result
    return str(data)

def format_rubric_advanced(rubric_json, features_json):
    lines = []
    
    # Process Rubric Scores
    try:
        rubric = json.loads(rubric_json) if isinstance(rubric_json, str) else rubric_json
        if rubric:
            lines.append("【Rubric Scores】")
            # Map of internal names to display names
            display_map = {
                'code_quality': 'Code Quality',
                'jd_relevance': 'JD Relevance',
                'complexity': 'Complexity',
                'best_practices': 'Best Practices'
            }
            for key, display in display_map.items():
                val = rubric.get(key, 0)
                lines.append(f"• {display}: {val}/25")
    except:
        pass

    # Process Strengths and Weaknesses from features
    try:
        features = json.loads(features_json) if isinstance(features_json, str) else features_json
        if features:
            strengths = features.get('strengths', [])
            weaknesses = features.get('weaknesses', [])
            
            if strengths:
                lines.append("\n【Key Strengths】")
                lines.extend([f"• {s}" for s in strengths if s])
                
            if weaknesses:
                lines.append("\n【Areas for Improvement】")
                lines.extend([f"• {w}" for w in weaknesses if w])
    except:
        pass

    return "\n".join(lines) if lines else "N/A"

def extract_repos(repos_json):
    if not repos_json:
        return "N/A"
    try:
        repos = json.loads(repos_json) if isinstance(repos_json, str) else repos_json
        links = []
        for repo in repos:
            if isinstance(repo, dict) and 'url' in repo:
                links.append(repo['url'])
            elif isinstance(repo, str):
                links.append(repo)
        return "\n".join(links) if links else "N/A"
    except:
        return "N/A"

def extract_recommendation_advanced(readiness_json):
    if not readiness_json:
        return "N/A"
    try:
        data = json.loads(readiness_json) if isinstance(readiness_json, str) else readiness_json
        sections = []
        
        exec_summary = data.get('executive_summary', [])
        if exec_summary:
            sections.append(format_list(exec_summary, "Executive Summary Findings"))
            
        risk_factors = data.get('risk_factors', [])
        skill_gaps = data.get('skill_gaps', [])
        combined_risks = []
        if risk_factors: combined_risks.extend(risk_factors)
        if skill_gaps: combined_risks.extend(skill_gaps)
        
        if combined_risks:
            sections.append(format_list(combined_risks, "Risk Factors & Gaps"))
            
        focus_areas = data.get('interview_focus_areas', [])
        if focus_areas:
            sections.append(format_list(focus_areas, "Interview Focus Areas"))
            
        return "\n".join(sections).strip() if sections else "N/A"
    except:
        return "N/A"

def extract_skeptic(skeptic_json):
    if not skeptic_json:
        return "N/A"
    try:
        data = json.loads(skeptic_json) if isinstance(skeptic_json, str) else skeptic_json
        concerns = data.get('major_concerns', [])
        risks = data.get('hidden_risks', [])
        combined = concerns + risks
        return format_list(combined)
    except:
        return "N/A"

def main():
    print(f"Connecting to database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Error: Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        wc.name,
        sr.resume_score,
        sr.github_score,
        sr.repo_count,
        sr.recommendation as hiring_justification,
        sr.repos_json as github_evidence,
        sr.rubric_scores_json as github_rubrics,
        sr.github_features_json as github_features,
        sr.interview_readiness_json as ai_recommendation,
        sr.skeptic_analysis_json as skeptic_audit,
        sr.justification_json
    FROM screening_results sr
    JOIN candidates c ON sr.candidate_id = c.id
    JOIN woxsen_candidates wc ON c.email = wc.email
    WHERE sr.github_score > 0
    """
    
    df_raw = pd.read_sql_query(query, conn)
    conn.close()

    if df_raw.empty:
        print("No candidates with GitHub scores found.")
        return

    def calculate_overall(row):
        try:
            rubric = json.loads(row['github_rubrics']) if row['github_rubrics'] else {}
            if rubric:
                return sum(rubric.values())
        except:
            pass
        return row['github_score']

    df_raw['calculated_github_score'] = df_raw.apply(calculate_overall, axis=1)
    top_10 = df_raw.sort_values(by='calculated_github_score', ascending=False).head(10).copy()

    export_data = []
    for _, row in top_10.iterrows():
        export_data.append({
            "Candidate Name": row['name'],
            "Resume Score": f"{int(row['resume_score'])}/100",
            "GitHub Score": f"{int(row['calculated_github_score'])}/100",
            "Total Repos": row['repo_count'],
            "Hiring Justification": format_list(row['justification_json']) if row['justification_json'] else row['hiring_justification'],
            "GitHub Evidence Tracking (Repo Links)": extract_repos(row['github_evidence']),
            "GitHub Rubrics & Analysis": format_rubric_advanced(row['github_rubrics'], row['github_features']),
            "AI Recommendation Summary": extract_recommendation_advanced(row['ai_recommendation']),
            "Skeptic Audit": extract_skeptic(row['skeptic_audit'])
        })

    df_export = pd.DataFrame(export_data)
    os.makedirs(DATA_DIR, exist_ok=True)
    output_file = os.path.join(DATA_DIR, "top_10_candidates_report.xlsx")
    
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    df_export.to_excel(writer, index=False, sheet_name='Top 10 Candidates')
    
    worksheet = writer.sheets['Top 10 Candidates']
    from openpyxl.styles import Alignment
    
    for idx, col in enumerate(df_export.columns):
        # Set column width
        worksheet.column_dimensions[chr(65 + idx)].width = 50
        # Enable text wrap for all cells in this column
        for cell in worksheet[chr(65 + idx)]:
            cell.alignment = Alignment(wrap_text=True, vertical='top')
        
    writer.close()
    print(f"Successfully exported refined top 10 candidates to: {output_file}")

if __name__ == "__main__":
    main()
