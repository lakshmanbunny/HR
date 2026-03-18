import json
from datetime import datetime
from typing import Dict, Any, Optional

class ReportService:
    def __init__(self):
        self.colors = {
            "primary": "#2286FE",
            "success": "#059669",
            "danger": "#DC2626",
            "warning": "#F59E0B",
            "text_main": "#1A1A1A",
            "text_muted": "#64748B",
            "bg_muted": "#F9FAFB",
            "bg_page": "#FFFFFF"
        }

    def generate_candidate_report(self, candidate_data: Dict[str, Any], evaluation_data: Dict[str, Any]) -> str:
        """
        Generates a self-contained HTML report for a candidate.
        """
        name = candidate_data.get("name", "Candidate")
        rank = candidate_data.get("rank", "N/A")
        score = evaluation_data.get("overall_score", 0)
        
        # Derived data
        decision = evaluation_data.get("final_decision", "PENDING")
        synthesis = evaluation_data.get("final_synthesized_decision") or {}
        justification = evaluation_data.get("justification") or []
        resume_score = evaluation_data.get("resume_score", 0)
        github_score = evaluation_data.get("github_score", 0)
        repo_count = evaluation_data.get("repo_count", 0)
        repos = evaluation_data.get("repos") or []
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candidate Report - {name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {self.colors['primary']};
            --success: {self.colors['success']};
            --danger: {self.colors['danger']};
            --warning: {self.colors['warning']};
            --text-main: {self.colors['text_main']};
            --text-muted: {self.colors['text_muted']};
            --bg-muted: {self.colors['bg_muted']};
            --bg-page: {self.colors['bg_page']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.5;
            padding: 40px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
        }}
        
        .candidate-info h1 {{
            font-size: 48px;
            font-weight: 900;
            letter-spacing: -0.02em;
        }}
        
        .candidate-info p {{
            font-size: 18px;
            color: var(--text-muted);
            font-weight: 500;
        }}
        
        .rank-badge {{
            background: var(--primary);
            color: white;
            padding: 10px 20px;
            border-radius: 16px;
            font-weight: 900;
            font-size: 24px;
            box-shadow: 0 10px 20px rgba(34, 134, 254, 0.2);
        }}
        
        .decision-card {{
            background: linear-gradient(to right, #2563EB, #4F46E5);
            border-radius: 32px;
            padding: 3px;
            margin-bottom: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
        }}
        
        .decision-inner {{
            background: white;
            border-radius: 30px;
            padding: 32px;
        }}
        
        .decision-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #F1F5F9;
            padding-bottom: 24px;
            margin-bottom: 24px;
        }}
        
        .status-label {{
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            color: var(--primary);
        }}
        
        .decision-text {{
            font-size: 32px;
            font-weight: 900;
            color: {self.colors['success'] if 'APPROVE' in decision else self.colors['danger'] if 'REJECT' in decision else self.colors['text_main']};
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: var(--bg-muted);
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 24px;
        }}
        
        .metric-label {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
        }}
        
        .section {{
            margin-bottom: 32px;
            background: white;
            border: 1px solid #F1F5F9;
            border-radius: 24px;
            overflow: hidden;
        }}
        
        .section-header {{
            padding: 24px;
            background: var(--bg-muted);
            font-size: 14px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #F1F5F9;
        }}
        
        .section-content {{
            padding: 24px;
        }}
        
        .bullet-list {{
            list-style: none;
        }}
        
        .bullet-item {{
            background: white;
            padding: 12px;
            border-radius: 12px;
            border: 1px solid #F8FAFC;
            margin-bottom: 12px;
            display: flex;
            gap: 12px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        
        .bullet-dot {{
            width: 8px;
            height: 8px;
            background: var(--primary);
            border-radius: 50%;
            margin-top: 6px;
        }}
        
        .github-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }}
        
        .repo-card {{
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 16px;
            transition: all 0.2s;
        }}
        
        .repo-name {{
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 4px;
        }}
        
        .repo-desc {{
            font-size: 11px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}
        
        .footer {{
            margin-top: 60px;
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            border-top: 1px solid #F1F5F9;
            padding-top: 24px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="candidate-info">
                <h1>{name}</h1>
                <p>Top-tier technical profile validated by AI Audit.</p>
            </div>
            <div>
                <div style="font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; text-align: right;">Global Rank</div>
                <div class="rank-badge">#{rank}</div>
            </div>
        </header>

        <section class="decision-card">
            <div class="decision-inner">
                <div class="decision-header">
                    <div>
                        <div class="status-label">Final Hiring Decision</div>
                        <div class="decision-text">{decision}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="status-label">Confidence</div>
                        <div style="font-size: 32px; font-weight: 900;">{synthesis.get('confidence', 'N/A')}%</div>
                    </div>
                </div>
                
                <div class="status-label" style="margin-bottom: 16px;">Executive Synthesis</div>
                <ul class="bullet-list">
                    {''.join([f'<li class="bullet-item"><div class="bullet-dot"></div><div style="font-size: 14px; font-weight: 500;">{item}</div></li>' for item in synthesis.get('decision_reasoning', justification or ["No specific reasoning provided."])])}
                </ul>
            </div>
        </section>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">📄 Resume Score</div>
                <div class="metric-value">{resume_score}/100</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">💻 GitHub Score</div>
                <div class="metric-value">{github_score}/100</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">📦 Repositories</div>
                <div class="metric-value">{repo_count} Total</div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">🏆 Hiring Justification</div>
            <div class="section-content">
                <ul class="bullet-list text-success">
                    {''.join([f'<li class="bullet-item" style="border-left-color: var(--success);"><div class="bullet-dot" style="background: var(--success);"></div><div style="font-size: 14px; font-weight: 500;">{item}</div></li>' for item in justification])}
                </ul>
            </div>
        </div>

        <div class="section">
            <div class="section-header">📂 GitHub Evidence Tracking</div>
            <div class="section-content">
                <div class="github-grid">
                    {''.join([f'<div class="repo-card"><div class="repo-name">{repo.get("name")}</div><div class="repo-desc">{repo.get("description", "No description")}</div><div style="font-size: 10px; font-weight: 700; color: var(--primary);">{repo.get("language", "")}</div></div>' for repo in repos[:6]])}
                </div>
            </div>
        </div>

        <div class="footer">
            Generated by ParadigmIT AI Recruitment Platform • {datetime.now().strftime("%B %d, %Y")}
        </div>
    </div>
</body>
</html>
"""
        return html

report_service = ReportService()
