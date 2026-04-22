import React from 'react';
import { useScreening } from '../../context/ScreeningContext';
import { Award, Code, Database, FileText, MessageSquare, ExternalLink, ShieldAlert, ShieldCheck, ChevronDown, ChevronRight, Github, Terminal, CheckCircle, RotateCw, Zap, ArrowLeft, Download } from 'lucide-react';
import CandidateGrid from './CandidateGrid';

const CollapsibleSection = ({ title, icon: Icon, children, defaultOpen = false, count }) => {
    const [isOpen, setIsOpen] = React.useState(defaultOpen);
    return (
        <div className={`flex flex-col border border-gray-100 rounded-3xl overflow-hidden transition-all duration-300 mb-6 ${isOpen ? 'bg-white shadow-xl shadow-gray-50' : 'bg-gray-50/50 hover:bg-white hover:shadow-md'}`}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center justify-between p-6 w-full text-left transition-colors"
            >
                <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-xl ${isOpen ? 'bg-primary-blue text-white' : 'bg-white border border-gray-100 text-gray-400'}`}>
                        <Icon size={20} />
                    </div>
                    <div className="flex items-center gap-3">
                        <h3 className="text-base font-black text-[#1A1A1A] uppercase tracking-wider">{title}</h3>
                        {count !== undefined && (
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${isOpen ? 'bg-blue-50 text-primary-blue' : 'bg-white text-gray-400 border border-gray-100'}`}>
                                {count}
                            </span>
                        )}
                    </div>
                </div>
                {isOpen ? <ChevronDown size={20} className="text-gray-400" /> : <ChevronRight size={20} className="text-gray-400" />}
            </button>
            {isOpen && (
                <div className="px-6 pb-8 pt-2 animate-in fade-in slide-in-from-top-2 duration-300">
                    {children}
                </div>
            )}
        </div>
    );
};

const BulletList = ({ items, variant = 'info' }) => {
    if (!items || !Array.isArray(items)) return null;
    return (
        <ul className="flex flex-col gap-3">
            {items.map((item, i) => (
                <li key={i} className="flex items-start gap-3 bg-white p-3 rounded-xl border border-gray-50 shadow-sm border-l-4 border-l-primary-blue/30">
                    <div className={`mt-1.5 shrink-0 w-1.5 h-1.5 rounded-full ${variant === 'success' ? 'bg-success-text' :
                        variant === 'danger' ? 'bg-red-500' :
                            variant === 'warning' ? 'bg-orange-500' : 'bg-primary-blue'
                        }`} />
                    <span className="text-sm font-medium text-slate-700 leading-relaxed">{item}</span>
                </li>
            ))}
        </ul>
    );
};

const Results = () => {
    const {
        results,
        selectedCandidateId,
        setSelectedCandidateId,
        submitHRDecision,
        runScreening,
        runStage2,
        runStage3,
        isRunningStage2,
        forceEvaluate,
        toggleRagOverride,
        isForceEvaluating
    } = useScreening();

    const [hrNotes, setHrNotes] = React.useState('');
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    // HR Configurable Evaluation Weights
    const [evaluationWeights, setEvaluationWeights] = React.useState({
        resume_match: 0.40,
        github_quality: 0.30,
        experience_depth: 0.15,
        skill_relevance: 0.15
    });

    if (!results) return null;

    // Derived data
    const selectedCandidate = results.evaluations[selectedCandidateId];
    const selectedCandidateBasic = results.ranking.find(c => c.candidate_id === selectedCandidateId);

    const downloadReport = async () => {
        if (!selectedCandidateId) return;
        const API_BASE = "/api";
        try {
            const response = await fetch(`${API_BASE}/candidate/${selectedCandidateId}/report-html`);
            if (response.ok) {
                const html = await response.text();
                const blob = new Blob([html], { type: 'text/html' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Report_${selectedCandidateBasic?.name.replace(/\s+/g, '_')}_${selectedCandidateId}.html`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            console.error("Download failed", error);
        }
    };
    if (!selectedCandidateId) {
        return (
            <div className="flex flex-col flex-1">
                {/* Stage 2 Button — at the top of candidate grid */}
                <div className="max-w-7xl w-full mx-auto px-6 pt-4">
                    {(() => {
                        const hasStage2Results = results?.ranking?.slice(0, 5).some(c => (results.evaluations[c.candidate_id]?.github_score || 0) > 0);

                        if (hasStage2Results) {
                            return (
                                <div className="p-5 bg-gradient-to-r from-indigo-900 to-indigo-800 rounded-2xl border border-indigo-700 flex items-center justify-between">
                                    <div className="flex flex-col gap-1">
                                        <h3 className="text-white text-sm font-black uppercase tracking-widest">Stage 3: Interview Readiness & Skeptic Agent</h3>
                                        <p className="text-indigo-300 text-xs font-medium">Deep-dive behavioral/technical readiness audit and adversarial skeptic analysis.</p>
                                    </div>
                                    <button
                                        onClick={() => typeof runStage3 === 'function' && runStage3()}
                                        disabled={isRunningStage2} // Re-use loading state if applicable
                                        className="px-6 py-3 bg-white text-indigo-900 text-[11px] font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg"
                                    >
                                        {isRunningStage2 ? (
                                            <><RotateCw size={14} className="animate-spin" /> Analyzing...</>
                                        ) : (
                                            <><ShieldCheck size={14} /> Run Stage 3</>
                                        )}
                                    </button>
                                </div>
                            );
                        }

                        return (
                            <div className="p-5 bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl border border-gray-700 flex items-center justify-between">
                                <div className="flex flex-col gap-1">
                                    <h3 className="text-white text-sm font-black uppercase tracking-widest">Stage 2: GitHub Verification</h3>
                                    <p className="text-gray-400 text-xs font-medium">Analyze top 60 candidates' GitHub repos with AI-powered code review (Gemini 2.5 Pro)</p>
                                </div>
                                <button
                                    onClick={() => runStage2()}
                                    disabled={isRunningStage2}
                                    className="px-6 py-3 bg-white text-gray-900 text-[11px] font-black uppercase tracking-widest rounded-xl hover:bg-gray-100 transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg"
                                >
                                    {isRunningStage2 ? (
                                        <><RotateCw size={14} className="animate-spin" /> Verifying...</>
                                    ) : (
                                        <><Github size={14} /> Run Stage 2</>
                                    )}
                                </button>
                            </div>
                        );
                    })()}
                </div>
                <CandidateGrid results={results} onSelectCandidate={setSelectedCandidateId} />
            </div>
        );
    }

    return (
        <div className="flex flex-col flex-1 overflow-hidden h-[calc(100vh-64px-60px)]">
            {/* Main Content - Full Width Detail View */}
            <main className="flex-1 bg-white overflow-y-auto">
                {selectedCandidate ? (
                    <div className="max-w-5xl mx-auto p-6 md:p-10 w-full">
                        <button
                            onClick={() => setSelectedCandidateId(null)}
                            className="mb-8 flex items-center gap-2 text-sm font-black uppercase tracking-widest text-gray-400 hover:text-primary-blue transition-colors group w-max"
                        >
                            <div className="bg-gray-50 border border-gray-100 p-1.5 rounded-lg group-hover:border-blue-100 group-hover:bg-blue-50 transition-colors">
                                <ArrowLeft size={16} />
                            </div>
                            Back to Pipeline Grid
                        </button>

                        {!selectedCandidate.final_synthesized_decision && (
                            <div className={`mb-8 p-4 rounded-2xl border flex flex-col md:flex-row items-center justify-between gap-4 shadow-sm transition-all duration-300 ${selectedCandidate.evaluation_blocked ? 'bg-red-50/50 border-red-100' : 'bg-blue-50/50 border-blue-100'}`}>
                                <div className="flex items-center gap-4">
                                    <div className={`p-2.5 rounded-xl shadow-sm ${selectedCandidate.evaluation_blocked ? 'bg-red-500 text-white' : 'bg-primary-blue text-white'}`}>
                                        {selectedCandidate.evaluation_blocked ? (
                                            <ShieldAlert size={20} />
                                        ) : (
                                            <ShieldCheck size={20} />
                                        )}
                                    </div>
                                    <div className="flex flex-col">
                                        <div className="flex items-center gap-2">
                                            <h3 className={`text-xs font-black uppercase tracking-[0.15em] ${selectedCandidate.evaluation_blocked ? 'text-red-700' : 'text-primary-blue'}`}>
                                                {selectedCandidate.evaluation_blocked ? 'Quality gate: blocked' : 'Quality gate: passed'}
                                            </h3>
                                            {selectedCandidate.evaluation_blocked && (
                                                <span className="px-1.5 py-0.5 bg-red-600 text-white text-[8px] font-black rounded uppercase">Quality Lock</span>
                                            )}
                                        </div>
                                        <p className="text-[11px] font-bold text-gray-500 leading-tight mt-0.5 max-w-md">
                                            {selectedCandidate.evaluation_blocked
                                                ? 'Stage 1 JD match below threshold. Use override or force re-run agents after review.'
                                                : 'Stage 1 metrics OK. Full agent pipeline can run.'}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={() => forceEvaluate(selectedCandidateId, evaluationWeights)}
                                        disabled={isForceEvaluating}
                                        className={`px-5 py-2.5 rounded-xl font-black text-[10px] uppercase tracking-widest shadow-sm transition-all flex items-center gap-2 ${selectedCandidate.evaluation_blocked
                                            ? 'bg-white text-red-600 border border-red-100 hover:bg-red-50'
                                            : 'bg-primary-blue text-white hover:bg-blue-700 shadow-blue-100'} disabled:opacity-50`}
                                    >
                                        {isForceEvaluating ? (
                                            <RotateCw size={14} className="animate-spin" />
                                        ) : selectedCandidate.evaluation_blocked ? (
                                            <Zap size={14} />
                                        ) : (
                                            <CheckCircle size={14} />
                                        )}
                                        {isForceEvaluating ? 'Evaluating...' : selectedCandidate.evaluation_blocked ? 'Force Run Agents' : 'Re-run pipeline'}
                                    </button>
                                </div>
                            </div>
                        )}

                        <header className="mb-10">
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                <div className="flex flex-col gap-1">
                                    <h1 className="text-3xl md:text-5xl font-black tracking-tight text-[#1A1A1A]">{selectedCandidateBasic?.name}</h1>
                                    <div className="flex items-center gap-4">
                                        <p className="text-xl text-gray-500 font-medium">Top-tier technical profile validated by AI Audit.</p>
                                        <button
                                            onClick={downloadReport}
                                            className="px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-500 hover:text-primary-blue hover:border-blue-100 hover:bg-blue-50 transition-all flex items-center gap-2 text-[10px] font-black uppercase tracking-widest"
                                        >
                                            <Download size={14} /> Download HTML
                                        </button>
                                    </div>
                                </div>
                                <div className="flex flex-col items-center md:items-end gap-2">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Global Rank</span>
                                    <div className="w-14 h-14 bg-primary-blue text-white rounded-2xl flex items-center justify-center text-2xl font-black shadow-lg shadow-blue-100">
                                        #{selectedCandidateBasic?.rank}
                                    </div>
                                </div>
                            </div>
                        </header>

                        {
                            selectedCandidate.final_synthesized_decision && (
                                <section className="mb-12">
                                    <div className="p-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-[2rem] shadow-xl shadow-blue-50">
                                        <div className="bg-white rounded-[1.9rem] p-8 md:p-10 flex flex-col gap-8">
                                            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
                                                <div className="flex items-center gap-4">
                                                    <div className="p-3 bg-blue-50 rounded-2xl text-primary-blue">
                                                        <ShieldCheck size={32} />
                                                    </div>
                                                    <div className="flex flex-col">
                                                        <span className="text-[11px] font-black text-primary-blue uppercase tracking-[0.2em]">Final Hiring Decision</span>
                                                        <h2 className={`text-3xl md:text-4xl font-black ${selectedCandidate.final_synthesized_decision.final_decision.includes('REJECT') || selectedCandidate.final_synthesized_decision.final_decision.includes('HOLD') ? 'text-red-600' : 'text-success-text'
                                                            }`}>
                                                            {selectedCandidate.hr_decision?.status === 'COMPLETED' ? `HR DECISION: ${selectedCandidate.hr_decision.decision}` : selectedCandidate.final_synthesized_decision.final_decision}
                                                        </h2>
                                                    </div>
                                                </div>
                                                <div className="flex flex-col items-end">
                                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                                                        {selectedCandidate.hr_decision?.status === 'COMPLETED' ? 'Decision Finalized' : 'Synthesis Confidence'}
                                                    </span>
                                                    <div className="text-3xl font-black text-[#1A1A1A]">
                                                        {selectedCandidate.hr_decision?.status === 'COMPLETED' ? '✓' : `${selectedCandidate.final_synthesized_decision.confidence}%`}
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex flex-col gap-6">
                                                <div className="flex items-center gap-2">
                                                    <div className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border ${selectedCandidate.final_synthesized_decision.risk_level === 'HIGH' ? 'bg-red-50 text-red-600 border-red-100' :
                                                        selectedCandidate.final_synthesized_decision.risk_level === 'MEDIUM' ? 'bg-orange-50 text-orange-600 border-orange-100' :
                                                            'bg-green-50 text-green-600 border-green-100'
                                                        }`}>
                                                        Risk Level: {selectedCandidate.final_synthesized_decision.risk_level}
                                                    </div>
                                                    <div className="px-3 py-1 bg-gray-50 text-gray-500 border border-gray-100 rounded-full text-[10px] font-bold uppercase tracking-widest">
                                                        Classification: {selectedCandidate.final_synthesized_decision.candidate_classification}
                                                    </div>
                                                </div>

                                                <div className="flex flex-col gap-4">
                                                    <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Executive Synthesis</h4>
                                                    <BulletList items={selectedCandidate.final_synthesized_decision.decision_reasoning} variant="info" />
                                                </div>
                                            </div>

                                        </div>
                                    </div>
                                </section>
                            )
                        }

                        <section className="mb-12">
                            <div className="p-1 bg-gradient-to-r from-gray-200 to-gray-300 rounded-[2rem] shadow-xl shadow-gray-50">
                                <div className="bg-white rounded-[1.9rem] p-8 md:p-10 flex flex-col gap-6">
                                    <div className="flex items-center justify-between">
                                        <div className="flex flex-col gap-1">
                                            <h4 className="text-sm font-black text-[#1A1A1A] uppercase tracking-wider">Human-In-The-Loop Action</h4>
                                            <p className="text-sm text-gray-500 font-medium">Review candidate metrics and finalize the hiring decision.</p>
                                        </div>
                                        {selectedCandidate.hr_decision?.status === 'COMPLETED' && (
                                            <div className="px-4 py-2 bg-success-light text-success-text rounded-xl font-black text-xs uppercase tracking-widest border border-success-text/20">
                                                Final Status: {selectedCandidate.hr_decision.decision}
                                            </div>
                                        )}
                                    </div>

                                    {selectedCandidate.hr_decision?.status !== 'COMPLETED' ? (
                                        <div className="flex flex-col gap-4">
                                            <textarea
                                                className="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl text-sm font-medium focus:ring-2 focus:ring-primary-blue focus:border-transparent transition-all outline-none"
                                                placeholder="Add internal notes for this decision..."
                                                rows={2}
                                                value={hrNotes}
                                                onChange={(e) => setHrNotes(e.target.value)}
                                            />
                                            <div className="flex items-center gap-3">
                                                <button
                                                    onClick={() => {
                                                        setIsSubmitting(true);
                                                        submitHRDecision(selectedCandidateId, 'APPROVE', hrNotes).finally(() => setIsSubmitting(false));
                                                    }}
                                                    disabled={isSubmitting}
                                                    className="flex-1 py-4 bg-success-text text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-100 disabled:opacity-50"
                                                >
                                                    Approve Candidate
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setIsSubmitting(true);
                                                        submitHRDecision(selectedCandidateId, 'HOLD', hrNotes).finally(() => setIsSubmitting(false));
                                                    }}
                                                    disabled={isSubmitting}
                                                    className="flex-1 py-4 bg-orange-500 text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-orange-600 transition-all shadow-lg shadow-orange-100 disabled:opacity-50"
                                                >
                                                    Hold for Review
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        setIsSubmitting(true);
                                                        submitHRDecision(selectedCandidateId, 'REJECT', hrNotes).finally(() => setIsSubmitting(false));
                                                    }}
                                                    disabled={isSubmitting}
                                                    className="flex-1 py-4 bg-red-600 text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-red-700 transition-all shadow-lg shadow-red-100 disabled:opacity-50"
                                                >
                                                    Reject Profile
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col gap-6">
                                            <div className="p-6 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                                                <div className="flex flex-col gap-2">
                                                    <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Decision Notes</div>
                                                    <p className="text-sm font-medium text-slate-700 italic">
                                                        {selectedCandidate.hr_decision.notes || "No additional notes provided."}
                                                    </p>
                                                    <div className="text-[10px] text-gray-400 mt-2">
                                                        Actioned on: {new Date(selectedCandidate.hr_decision.timestamp).toLocaleString()}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Interview Trigger Orchestration Phase 8 */}
                                            {selectedCandidate.hr_decision.decision === 'APPROVE' && (
                                                <div className="pt-6 border-t border-gray-200 flex flex-col gap-4">
                                                    <div className="flex items-center justify-between">
                                                        <h4 className="text-sm font-black text-[#1A1A1A] uppercase tracking-wider">Dynamic Interview Action</h4>
                                                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${selectedCandidate.interview_status === 'PENDING' ? 'bg-orange-50 text-orange-600' :
                                                            selectedCandidate.interview_status === 'APPROVED' ? 'bg-blue-50 text-blue-600' :
                                                                selectedCandidate.interview_status === 'INTERVIEW_SENT' ? 'bg-indigo-50 text-indigo-600' :
                                                                    'bg-green-50 text-green-600'
                                                            }`}>
                                                            {selectedCandidate.interview_status?.replace('_', ' ')}
                                                        </span>
                                                    </div>

                                                    {selectedCandidate.interview_status === 'PENDING' && (
                                                        <button
                                                            onClick={async () => {
                                                                setIsSubmitting(true);
                                                                const API_BASE = "/api";
                                                                try {
                                                                    const res = await fetch(`${API_BASE}/candidate/${selectedCandidateId}/approve-interview`, { method: 'POST' });
                                                                    if (res.ok) alert("Interview Approved & Sent!");
                                                                    runScreening(evaluationWeights);
                                                                } catch (e) { console.error(e) }
                                                                finally { setIsSubmitting(false); }
                                                            }}
                                                            disabled={isSubmitting || selectedCandidate.evaluation_locked}
                                                            className="w-full py-4 bg-primary-blue text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-blue-700 transition-all shadow-lg shadow-blue-100 disabled:opacity-50"
                                                        >
                                                            {isSubmitting ? 'Processing...' : 'Approve for LiveKit Interview'}
                                                        </button>
                                                    )}

                                                    {selectedCandidate.interview_status === 'INTERVIEW_SENT' && (
                                                        <div className="flex flex-col gap-2">
                                                            <p className="text-xs text-gray-500 font-medium text-center">Invitation sent to candidate's email. Waiting for them to join.</p>
                                                            <button
                                                                onClick={() => alert("Simulated Resend")}
                                                                className="w-full py-3 bg-white text-primary-blue border border-primary-blue rounded-xl font-bold text-sm uppercase tracking-wider hover:bg-blue-50 transition-all"
                                                            >
                                                                Resend Invite
                                                            </button>
                                                        </div>
                                                    )}

                                                    {selectedCandidate.interview_status === 'INTERVIEW_COMPLETED' && (
                                                        <button
                                                            onClick={() => window.open(`/interview-results/${selectedCandidate.interview_session_id}`, '_blank')}
                                                            className="w-full py-4 bg-black text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-gray-800 transition-all shadow-lg shadow-gray-200"
                                                        >
                                                            View LiveKit Interview Results
                                                        </button>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </section>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                            <div className="p-6 bg-bg-muted border border-gray-200 rounded-2xl">
                                <div className="flex items-center gap-2 text-gray-500 text-[13px] font-bold mb-2">
                                    <FileText size={16} />
                                    <span>Resume Score</span>
                                </div>
                                <div className="text-3xl font-bold">{selectedCandidate.resume_score}/100</div>
                            </div>
                            <div className="p-6 bg-bg-muted border border-gray-200 rounded-2xl">
                                <div className="flex items-center gap-2 text-gray-500 text-[13px] font-bold mb-2">
                                    <Database size={16} />
                                    <span>GitHub Score</span>
                                </div>
                                <div className="text-3xl font-bold">{selectedCandidate.github_score}/100</div>
                            </div>
                            <div className="p-6 bg-bg-muted border border-gray-200 rounded-2xl">
                                <div className="flex items-center gap-2 text-gray-500 text-[13px] font-bold mb-2">
                                    <Code size={16} />
                                    <span>Repositories</span>
                                </div>
                                <div className="text-3xl font-bold">{selectedCandidate.repo_count} Total</div>
                            </div>
                        </div>

                        <CollapsibleSection title="Hiring Justification" icon={Award}>
                            <BulletList items={selectedCandidate.justification} variant="success" />
                        </CollapsibleSection>

                        {/* Resume Content Section */}
                        {selectedCandidate.raw_resume_text && (
                            <CollapsibleSection title="Resume Content" icon={FileText} defaultOpen={false}>
                                <div className="flex flex-col gap-4">
                                    {(() => {
                                        try {
                                            const parsed = JSON.parse(selectedCandidate.raw_resume_text);
                                            return (
                                                <>
                                                    {parsed.document_title && (
                                                        <div className="pb-3 border-b border-gray-100">
                                                            <h4 className="text-lg font-black text-[#1A1A1A]">{parsed.document_title}</h4>
                                                        </div>
                                                    )}
                                                    {parsed.sections?.map((section, idx) => (
                                                        <div key={idx} className="flex flex-col gap-2">
                                                            <div className="flex items-center gap-2">
                                                                <span className="px-2 py-0.5 bg-blue-50 text-primary-blue text-[9px] font-black uppercase tracking-widest rounded">
                                                                    {section.heading}
                                                                </span>
                                                            </div>
                                                            <div className="text-[13px] text-gray-700 leading-relaxed whitespace-pre-line pl-2 border-l-2 border-blue-100">
                                                                {section.content}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </>
                                            );
                                        } catch {
                                            return (
                                                <div className="text-[13px] text-gray-700 leading-relaxed whitespace-pre-line">
                                                    {selectedCandidate.raw_resume_text}
                                                </div>
                                            );
                                        }
                                    })()}
                                </div>
                            </CollapsibleSection>
                        )}

                        {/* GitHub Evidence — only shows after Stage 2 */}
                        {selectedCandidate.github_score > 0 && (
                            <>
                                {/* GitHub Repo Links */}
                                {selectedCandidate.repos?.length > 0 && (
                                    <CollapsibleSection title="GitHub Evidence Tracking" icon={Github} defaultOpen={true} count={selectedCandidate.repos.length}>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            {selectedCandidate.repos.map((repo, idx) => (
                                                <a key={idx} href={repo.url} target="_blank" rel="noopener noreferrer"
                                                    className="p-4 border border-gray-200 rounded-2xl hover:border-blue-300 hover:shadow-md transition-all group">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <Github size={16} className="text-gray-400 group-hover:text-primary-blue transition-colors" />
                                                        <span className="text-sm font-bold text-[#1A1A1A] group-hover:text-primary-blue transition-colors">{repo.name}</span>
                                                    </div>
                                                    <p className="text-[11px] text-gray-500 leading-relaxed mb-3 line-clamp-2">{repo.description || 'No description'}</p>
                                                    <div className="flex items-center gap-3 text-[10px] font-bold text-gray-400">
                                                        {repo.language && <span className="px-2 py-0.5 bg-blue-50 text-primary-blue rounded">{repo.language}</span>}
                                                        {repo.stars > 0 && <span>⭐ {repo.stars}</span>}
                                                        <ExternalLink size={10} className="ml-auto text-gray-300 group-hover:text-primary-blue" />
                                                    </div>
                                                </a>
                                            ))}
                                        </div>
                                    </CollapsibleSection>
                                )}

                                {/* GitHub Rubric Scores */}
                                {(selectedCandidate.github_rubric || (typeof selectedCandidate.github_features === 'object' && selectedCandidate.github_features?.rubric_scores)) && (() => {
                                    const rubric = selectedCandidate.github_rubric || selectedCandidate.github_features?.rubric_scores || {};
                                    const strengths = selectedCandidate.github_strengths || selectedCandidate.github_features?.strengths || [];
                                    const weaknesses = selectedCandidate.github_weaknesses || selectedCandidate.github_features?.weaknesses || [];
                                    const justification = selectedCandidate.github_justification || selectedCandidate.github_features?.github_justification || '';
                                    return (
                                        <CollapsibleSection title="GitHub Rubric & Analysis" icon={Code} defaultOpen={true}>
                                            <div className="flex flex-col gap-6">
                                                {/* Rubric Score Cards */}
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                    {[
                                                        { label: 'Code Quality', value: rubric.code_quality || 0, max: 25 },
                                                        { label: 'JD Relevance', value: rubric.jd_relevance || 0, max: 25 },
                                                        { label: 'Complexity', value: rubric.complexity || 0, max: 25 },
                                                        { label: 'Best Practices', value: rubric.best_practices || 0, max: 25 },
                                                    ].map((m, i) => {
                                                        const pct = (m.value / m.max) * 100;
                                                        const color = pct >= 70 ? 'text-green-600 bg-green-50 border-green-100' : pct >= 40 ? 'text-orange-600 bg-orange-50 border-orange-100' : 'text-red-600 bg-red-50 border-red-100';
                                                        return (
                                                            <div key={i} className={`p-4 rounded-2xl border flex flex-col gap-1.5 ${color}`}>
                                                                <div className="text-[10px] font-bold uppercase tracking-wider opacity-70">{m.label}</div>
                                                                <div className="text-2xl font-black">{m.value}/{m.max}</div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>

                                                {/* Justification */}
                                                {justification && (
                                                    <p className="text-[13px] text-gray-600 leading-relaxed italic border-l-2 border-gray-200 pl-3">{justification}</p>
                                                )}

                                                {/* Strengths */}
                                                {strengths.length > 0 && (
                                                    <div>
                                                        <h5 className="text-[10px] font-black text-green-600 uppercase tracking-widest mb-2">Strengths</h5>
                                                        <BulletList items={strengths} variant="success" />
                                                    </div>
                                                )}

                                                {/* Weaknesses */}
                                                {weaknesses.length > 0 && (
                                                    <div>
                                                        <h5 className="text-[10px] font-black text-orange-600 uppercase tracking-widest mb-2">Weaknesses</h5>
                                                        <BulletList items={weaknesses} variant="warning" />
                                                    </div>
                                                )}
                                            </div>
                                        </CollapsibleSection>
                                    );
                                })()}

                                {/* AI Code Transparency — Show actual code */}
                                {selectedCandidate.code_evidence?.length > 0 && (
                                    <CollapsibleSection title="AI Code Transparency" icon={Terminal} defaultOpen={false} count={selectedCandidate.code_evidence.length}>
                                        <div className="flex flex-col gap-4">
                                            {selectedCandidate.code_evidence.map((ev, idx) => (
                                                <div key={idx} className="border border-gray-200 rounded-xl overflow-hidden">
                                                    <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200">
                                                        <div className="flex items-center gap-2">
                                                            <Github size={12} className="text-gray-400" />
                                                            <span className="text-[11px] font-bold text-gray-700">{ev.repo_name}/{ev.file_path}</span>
                                                            <span className="px-1.5 py-0.5 bg-blue-50 text-primary-blue text-[9px] font-bold rounded">{ev.language}</span>
                                                        </div>
                                                        <a href={ev.file_url} target="_blank" rel="noopener noreferrer"
                                                            className="text-[10px] font-bold text-gray-400 hover:text-primary-blue flex items-center gap-1">
                                                            View on GitHub <ExternalLink size={10} />
                                                        </a>
                                                    </div>
                                                    <pre className="p-4 text-[11px] leading-relaxed text-gray-700 bg-gray-900 text-gray-300 overflow-x-auto max-h-[300px] overflow-y-auto font-mono">
                                                        <code>{ev.code_snippet}</code>
                                                    </pre>
                                                </div>
                                            ))}
                                        </div>
                                    </CollapsibleSection>
                                )}
                            </>
                        )}

                        {
                            selectedCandidate.interview_readiness && (
                                <CollapsibleSection title="AI Recommendation Summary" icon={MessageSquare} count={selectedCandidate.interview_readiness.risk_factors.length + selectedCandidate.interview_readiness.skill_gaps.length}>
                                    <div className="flex flex-col gap-8">
                                        <div className="flex flex-wrap items-center justify-between gap-4 p-6 bg-gray-50 rounded-2xl border border-gray-100">
                                            <div className="flex flex-col">
                                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Status</span>
                                                <div className={`text-lg font-extrabold ${selectedCandidate.interview_readiness.hire_readiness_level === 'HIGH' ? 'text-success-text' :
                                                    selectedCandidate.interview_readiness.hire_readiness_level === 'MEDIUM' ? 'text-blue-600' : 'text-orange-500'
                                                    }`}>
                                                    {selectedCandidate.interview_readiness.hire_readiness_level} READY
                                                </div>
                                            </div>
                                            <div className="flex flex-col text-right">
                                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Confidence</span>
                                                <div className="text-lg font-extrabold text-[#1A1A1A]">
                                                    {selectedCandidate.interview_readiness.confidence_score}%
                                                </div>
                                            </div>
                                            <div className="flex flex-col text-right">
                                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Recommendation</span>
                                                <div className="px-3 py-1 bg-white rounded text-xs font-bold text-slate-700 ring-1 ring-gray-100">
                                                    {selectedCandidate.interview_readiness.final_hiring_recommendation}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="flex flex-col gap-4">
                                                <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Risk Factors & Gaps</h4>
                                                <BulletList items={[...selectedCandidate.interview_readiness.risk_factors, ...selectedCandidate.interview_readiness.skill_gaps]} variant="danger" />
                                            </div>
                                            <div className="flex flex-col gap-4">
                                                <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Interview Focus Areas</h4>
                                                <BulletList items={selectedCandidate.interview_readiness.interview_focus_areas} variant="info" />
                                            </div>
                                        </div>

                                        <div className="flex flex-col gap-4 border-t border-gray-100 pt-6">
                                            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Executive Summary Findings</h4>
                                            <BulletList items={selectedCandidate.interview_readiness.executive_summary} variant="success" />
                                        </div>

                                    </div>
                                </CollapsibleSection>
                            )
                        }

                        {
                            selectedCandidate.skeptic_analysis && (
                                <CollapsibleSection title="AI Skeptic Audit" icon={ShieldAlert} count={selectedCandidate.skeptic_analysis.major_concerns.length}>
                                    <div className="flex flex-col gap-8">
                                        <div className="flex items-center justify-between p-6 bg-orange-50 rounded-2xl border border-orange-100">
                                            <div className="flex flex-col">
                                                <span className="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Risk Severity Level</span>
                                                <div className={`text-lg font-black ${selectedCandidate.skeptic_analysis.risk_level === 'HIGH' ? 'text-orange-700' : 'text-orange-500'}`}>
                                                    {selectedCandidate.skeptic_analysis.risk_level}
                                                </div>
                                            </div>
                                            <div className="px-4 py-2 bg-white border border-orange-100 rounded-xl text-[10px] font-black text-orange-600 uppercase tracking-widest">
                                                Adversarial Probe: Active
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="flex flex-col gap-4">
                                                <h4 className="text-[10px] font-black text-orange-400 uppercase tracking-widest">Major Concerns</h4>
                                                <BulletList items={selectedCandidate.skeptic_analysis.major_concerns} variant="danger" />
                                            </div>
                                            <div className="flex flex-col gap-4">
                                                <h4 className="text-[10px] font-black text-orange-400 uppercase tracking-widest">Hidden Risks</h4>
                                                <BulletList items={selectedCandidate.skeptic_analysis.hidden_risks} variant="warning" />
                                            </div>
                                        </div>

                                        <div className="flex flex-col gap-4 border-t border-orange-100 pt-6">
                                            <h4 className="text-[10px] font-black text-orange-400 uppercase tracking-widest">Skeptic Warnings</h4>
                                            <BulletList items={selectedCandidate.skeptic_analysis.skeptic_recommendation} variant="danger" />
                                        </div>

                                    </div>
                                </CollapsibleSection>
                            )
                        }


                    </div >
                ) : (
                    <div className="max-w-5xl mx-auto p-6 md:p-10 w-full flex flex-col items-center justify-center gap-4 h-full">
                        <RotateCw size={24} className="animate-spin text-gray-300" />
                        <p className="text-sm text-gray-400 font-bold">Loading candidate data...</p>
                        <button onClick={() => setSelectedCandidateId(null)} className="text-xs font-bold text-primary-blue hover:underline mt-2">← Back to Pipeline Grid</button>
                    </div>
                )}
            </main >
        </div >
    );
};

// Results component export
export default Results;
