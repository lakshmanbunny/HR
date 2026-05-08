import React, { useState, useEffect } from 'react';
import { Search, User, FileText, AlertTriangle, CheckCircle2, ShieldAlert, Zap, Loader2, ChevronRight, MessageSquareQuote, Upload, Download, CheckSquare, Square, Trophy, FileCheck } from 'lucide-react';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const CandidatesPage = () => {
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCandidate, setSelectedCandidate] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [managerAnalysis, setManagerAnalysis] = useState(null);
    const [analyzingId, setAnalyzingId] = useState(null);
    const [isDirectUpload, setIsDirectUpload] = useState(false);
    const [intelligenceMode, setIntelligenceMode] = useState('recruiter'); // 'recruiter' or 'manager'
    const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
    const [auditFiles, setAuditFiles] = useState({ resume: null, jd: null });
    
    // Checkbox state for questions
    const [checkedQuestions, setCheckedQuestions] = useState({});

    const API_BASE = "/api/opencats";

    useEffect(() => {
        fetchCandidates();
    }, []);

    const fetchCandidates = async () => {
        try {
            const response = await fetch(`${API_BASE}/candidates`);
            if (response.ok) {
                const data = await response.json();
                setCandidates(data);
            }
        } catch (error) {
            console.error("Failed to fetch candidates", error);
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyze = async (candidateId) => {
        setIsDirectUpload(false);
        setAnalyzingId(candidateId);
        setAnalysis(null);
        setManagerAnalysis(null);
        setCheckedQuestions({});
        setIntelligenceMode('recruiter');
        
        try {
            const response = await fetch(`${API_BASE}/candidates/${candidateId}/analysis`);
            if (response.ok) {
                const data = await response.json();
                setAnalysis(data);
                const cand = candidates.find(c => c.id === candidateId);
                setSelectedCandidate(cand);
            }
        } catch (error) {
            console.error("Analysis failed", error);
        } finally {
            setAnalyzingId(null);
        }
    };

    const handleManagerAnalyze = async () => {
        if (!selectedCandidate) return;
        setAnalyzingId(selectedCandidate.id);
        setManagerAnalysis(null);
        
        try {
            const response = await fetch(`${API_BASE}/candidates/${selectedCandidate.id}/managerial-analysis`);
            if (response.ok) {
                const data = await response.json();
                setManagerAnalysis(data);
                setIntelligenceMode('manager');
            }
        } catch (error) {
            console.error("Managerial analysis failed", error);
        } finally {
            setAnalyzingId(null);
        }
    };

    const handleDirectUploadSubmit = async () => {
        if (!auditFiles.resume || !auditFiles.jd) {
            alert("Please upload both Resume and JD");
            return;
        }

        setIsDirectUpload(true);
        setSelectedCandidate({ name: auditFiles.resume.name.split('.')[0], id: 'GUEST' });
        setAnalyzingId('DIRECT');
        setAnalysis(null);
        setManagerAnalysis(null);
        setCheckedQuestions({});
        setIntelligenceMode('recruiter');
        setIsAuditModalOpen(false);

        const formData = new FormData();
        formData.append('resume', auditFiles.resume);
        formData.append('jd', auditFiles.jd);

        try {
            const response = await fetch(`${API_BASE}/analyze-direct`, {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                const data = await response.json();
                setAnalysis(data);
            }
        } catch (err) {
            console.error("Direct upload analysis failed", err);
        } finally {
            setAnalyzingId(null);
            setAuditFiles({ resume: null, jd: null });
        }
    };

    const toggleQuestion = (index) => {
        setCheckedQuestions(prev => ({
            ...prev,
            [index]: !prev[index]
        }));
    };

    const handleDownloadReport = () => {
        if (intelligenceMode === 'recruiter' && !analysis) return;
        if (intelligenceMode === 'manager' && !managerAnalysis) return;

        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        
        // Header
        doc.setFillColor(10, 15, 30);
        doc.rect(0, 0, pageWidth, 40, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.text(intelligenceMode === 'recruiter' ? "Technical Interview Sheet" : "Managerial Intelligence Audit", 20, 25);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(`Candidate: ${selectedCandidate?.name || 'Unknown'}`, 20, 33);
        doc.text(`Date: ${new Date().toLocaleDateString()}`, pageWidth - 60, 33);

        if (intelligenceMode === 'recruiter') {
            const successCount = Object.values(checkedQuestions).filter(Boolean).length;
            doc.setTextColor(0, 0, 0);
            doc.text(`Performance Score: ${successCount} / 10`, 20, 55);
            if (analysis.match_score) {
                doc.text(`Match Score (vs JD): ${analysis.match_score}%`, pageWidth - 60, 55);
            }
            
            const tableData = analysis.initial_call_questions.map((q, i) => [
                i + 1,
                checkedQuestions[i] ? "PASS" : "FAIL/NO",
                {
                    content: `${typeof q === 'string' ? q : q.question}\n\nHR CHEAT SHEET:\n${q.expected_answer || 'N/A'}`,
                    styles: { fontSize: 9 }
                }
            ]);

            autoTable(doc, {
                startY: 65,
                head: [['#', 'Status', 'Question & Verification Guide']],
                body: tableData,
                headStyles: { fillColor: [0, 102, 255] },
                margin: { top: 60 }
            });
        } else {
            // Managerial Report
            doc.setTextColor(0, 0, 0);
            doc.setFontSize(12);
            doc.text("Executive L1 Summary:", 20, 55);
            doc.setFontSize(9);
            const splitSummary = doc.splitTextToSize(managerAnalysis.l1_summary, pageWidth - 40);
            doc.text(splitSummary, 20, 62);

            let yPos = 62 + (splitSummary.length * 5) + 10;
            
            doc.setFontSize(12);
            doc.setFont('helvetica', 'bold');
            doc.text("The Gap (Inconsistencies):", 20, yPos);
            yPos += 7;
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            managerAnalysis.the_gap.forEach(item => {
                doc.text(`• ${item}`, 25, yPos);
                yPos += 5;
            });
        }

        doc.save(`${intelligenceMode === 'recruiter' ? 'Recruiter' : 'Manager'}_Audit_${selectedCandidate?.name.replace(/\s+/g, '_')}.pdf`);
    };

    const filteredCandidates = candidates.filter(c => 
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        (c.skills && c.skills.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="flex flex-col gap-8 pb-10">
            {/* Direct Audit Modal */}
            {isAuditModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setIsAuditModalOpen(false)}></div>
                    <div className="bg-white w-full max-w-lg rounded-[3rem] shadow-2xl relative z-10 overflow-hidden animate-in zoom-in duration-300">
                        <div className="bg-[#0A0F1E] p-10 text-white">
                            <h3 className="text-2xl font-black uppercase tracking-widest">New AI Audit</h3>
                            <p className="text-sm text-gray-400 mt-2">Upload Resume and JD for comparative screening.</p>
                        </div>
                        <div className="p-10 flex flex-col gap-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-text-muted">1. Candidate Resume (PDF/DOCX)</label>
                                <div className={`border-2 border-dashed rounded-2xl p-6 transition-all flex flex-col items-center gap-3 ${auditFiles.resume ? 'border-success bg-success/5' : 'border-gray-200 hover:border-primary-blue'}`}>
                                    <input type="file" accept=".pdf,.docx" className="hidden" id="resume-up" onChange={(e) => setAuditFiles(prev => ({ ...prev, resume: e.target.files[0] }))} />
                                    <label htmlFor="resume-up" className="cursor-pointer flex flex-col items-center gap-2">
                                        <Upload className={auditFiles.resume ? 'text-success' : 'text-text-muted'} size={32} />
                                        <span className="text-xs font-bold">{auditFiles.resume ? auditFiles.resume.name : 'Select Resume'}</span>
                                    </label>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-text-muted">2. Job Description (PDF/DOCX)</label>
                                <div className={`border-2 border-dashed rounded-2xl p-6 transition-all flex flex-col items-center gap-3 ${auditFiles.jd ? 'border-success bg-success/5' : 'border-gray-200 hover:border-primary-blue'}`}>
                                    <input type="file" accept=".pdf,.docx" className="hidden" id="jd-up" onChange={(e) => setAuditFiles(prev => ({ ...prev, jd: e.target.files[0] }))} />
                                    <label htmlFor="jd-up" className="cursor-pointer flex flex-col items-center gap-2">
                                        <FileText className={auditFiles.jd ? 'text-success' : 'text-text-muted'} size={32} />
                                        <span className="text-xs font-bold">{auditFiles.jd ? auditFiles.jd.name : 'Select JD'}</span>
                                    </label>
                                </div>
                            </div>

                            <button 
                                onClick={handleDirectUploadSubmit}
                                disabled={!auditFiles.resume || !auditFiles.jd}
                                className="w-full py-4 bg-primary-blue text-white rounded-2xl font-black uppercase tracking-widest hover:bg-primary-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-blue-100 mt-4"
                            >
                                Start Comparative Audit
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-[#0A0F1E] tracking-tight">Candidate Intelligence</h1>
                    <p className="text-sm text-text-muted mt-1 font-medium italic">Sourced directly from OpenCATS Database</p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="relative w-full md:w-96">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" size={18} />
                        <input 
                            type="text"
                            placeholder="Search by name or skills..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-12 pr-4 py-3.5 bg-white border border-border-subtle rounded-2xl text-sm font-medium focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue transition-all outline-none shadow-sm"
                        />
                    </div>
                    
                    <button 
                        onClick={() => setIsAuditModalOpen(true)}
                        className="flex items-center gap-2 px-6 py-3.5 bg-primary-blue text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-primary-dark transition-all active:scale-95 shadow-xl shadow-blue-100"
                    >
                        <Upload size={16} />
                        New AI Audit
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Candidate List */}
                <div className="lg:col-span-1 flex flex-col gap-4">
                    <div className="bg-white border border-border-subtle rounded-[2rem] overflow-hidden shadow-sm">
                        <div className="p-6 border-b border-border-subtle bg-bg-muted/30">
                            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-text-muted">OpenCATS Repository ({filteredCandidates.length})</h3>
                        </div>
                        <div className="max-h-[600px] overflow-y-auto custom-scrollbar">
                            {loading ? (
                                <div className="p-10 flex flex-col items-center justify-center gap-4">
                                    <Loader2 className="animate-spin text-primary-blue" size={32} />
                                    <span className="text-xs font-bold text-text-muted uppercase tracking-widest">Querying DB...</span>
                                </div>
                            ) : filteredCandidates.length === 0 ? (
                                <div className="p-10 text-center text-text-muted italic text-sm">No candidates found</div>
                            ) : (
                                filteredCandidates.map(candidate => (
                                    <div 
                                        key={candidate.id}
                                        onClick={() => handleAnalyze(candidate.id)}
                                        className={`p-5 border-b border-border-subtle last:border-0 cursor-pointer transition-all hover:bg-primary-blue/[0.02] group relative ${selectedCandidate?.id === candidate.id && !isDirectUpload ? 'bg-primary-blue/[0.04]' : ''}`}
                                    >
                                        <div className="flex items-start gap-4">
                                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors ${(selectedCandidate?.id === candidate.id && !isDirectUpload) ? 'bg-primary-blue text-white' : 'bg-bg-muted text-text-muted group-hover:bg-primary-blue/10 group-hover:text-primary-blue'}`}>
                                                <User size={20} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className="font-bold text-[#0A0F1E] truncate">{candidate.name}</h4>
                                                <p className="text-xs text-text-muted truncate mt-0.5">{candidate.email || 'No Email'}</p>
                                            </div>
                                            <div className="flex flex-col items-end gap-2">
                                                <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter">ID: {candidate.id}</span>
                                                {analyzingId === candidate.id ? (
                                                    <Loader2 className="animate-spin text-primary-blue" size={16} />
                                                ) : (
                                                    <ChevronRight size={16} className={`transition-transform ${(selectedCandidate?.id === candidate.id && !isDirectUpload) ? 'translate-x-1 text-primary-blue' : 'text-gray-300'}`} />
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Analysis Display */}
                <div className="lg:col-span-3">
                    {!selectedCandidate && !analyzingId ? (
                        <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white border border-dashed border-border-subtle rounded-[2.5rem] text-center p-10 group">
                            <div className="w-20 h-20 bg-bg-muted rounded-[2rem] flex items-center justify-center text-text-muted mb-6 group-hover:scale-110 transition-transform duration-500">
                                <Zap size={32} />
                            </div>
                            <h3 className="text-xl font-black text-[#0A0F1E]">Select a candidate or upload a resume</h3>
                            <p className="text-sm text-text-muted mt-2 max-w-sm font-medium italic">
                                Our AI Agent will provide a deep-dive Risk & Strength audit using Gemini 2.0 Flash.
                            </p>
                        </div>
                    ) : (analyzingId && (analyzingId === 'DIRECT' || analyzingId > 0)) ? (
                        <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white border border-border-subtle rounded-[2.5rem] p-10 relative overflow-hidden shadow-2xl shadow-blue-100/20">
                            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(0,102,255,0.05)_0%,_transparent_70%)] animate-pulse"></div>
                            <div className="z-10 flex flex-col items-center gap-6">
                                <div className="relative">
                                    <div className="w-24 h-24 border-4 border-primary-blue/10 border-t-primary-blue rounded-full animate-spin"></div>
                                    <div className="absolute inset-0 flex items-center justify-center text-primary-blue">
                                        <Zap size={32} className="animate-pulse" />
                                    </div>
                                </div>
                                <div className="text-center">
                                    <h3 className="text-xl font-black text-[#0A0F1E] uppercase tracking-widest">Intelligence Extraction</h3>
                                    <p className="text-sm text-text-muted mt-2 font-bold animate-pulse">Consulting Gemini 2.0 Flash...</p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-6 animate-in fade-in zoom-in duration-500">
                            {/* Candidate Header */}
                            <div className="bg-white p-8 rounded-[2.5rem] border border-border-subtle shadow-sm">
                                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                                    <div className="flex items-center gap-6">
                                        <div className="w-16 h-16 bg-primary-blue rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-200 relative">
                                            {isDirectUpload ? <FileText size={32} /> : <User size={32} />}
                                            {analysis?.match_score && (
                                                <div className="absolute -top-2 -right-2 w-8 h-8 bg-success rounded-full flex items-center justify-center text-[10px] font-black text-white border-2 border-white">
                                                    {analysis.match_score}
                                                </div>
                                            )}
                                        </div>
                                        <div>
                                            <h2 className="text-2xl font-black text-[#0A0F1E] truncate max-w-[400px]">{selectedCandidate.name}</h2>
                                            <div className="flex items-center gap-4 mt-1">
                                                <span className="text-xs font-bold text-text-muted flex items-center gap-1.5">
                                                    <CheckCircle2 size={14} className="text-success" /> {isDirectUpload ? 'Comparative Audit' : 'OpenCATS Profile'}
                                                </span>
                                                <span className="text-xs font-bold text-success-text flex items-center gap-1.5 px-2 py-0.5 bg-success/10 rounded-full">
                                                    <Zap size={10} /> Gemini 2.0 Flash Verified
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Tab Switcher */}
                                    <div className="bg-bg-muted p-1.5 rounded-2xl flex items-center self-stretch md:self-auto">
                                        <button 
                                            onClick={() => setIntelligenceMode('recruiter')}
                                            className={`px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${intelligenceMode === 'recruiter' ? 'bg-white text-primary-blue shadow-sm' : 'text-text-muted hover:text-primary-blue'}`}
                                        >
                                            Recruiter View
                                        </button>
                                        <button 
                                            onClick={() => {
                                                if (managerAnalysis) {
                                                    setIntelligenceMode('manager');
                                                } else {
                                                    handleManagerAnalyze();
                                                }
                                            }}
                                            className={`px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all ${intelligenceMode === 'manager' ? 'bg-primary-blue text-white shadow-sm' : 'text-text-muted hover:text-primary-blue'}`}
                                        >
                                            Manager View
                                        </button>
                                    </div>
                                </div>
                                
                                <div className="mt-8 pt-8 border-t border-border-subtle flex items-center justify-between">
                                    <div className="flex gap-2">
                                        {intelligenceMode === 'manager' && !managerAnalysis ? (
                                            <div className="flex items-center gap-2 text-primary-blue font-bold text-xs animate-pulse">
                                                <Loader2 className="animate-spin" size={14} /> Fetching L1 Transcript...
                                            </div>
                                        ) : (
                                            <div className="flex flex-col gap-1">
                                                <p className="text-xs text-text-muted font-medium italic">
                                                    {intelligenceMode === 'recruiter' ? "Focused on screening and initial technical verification." : "Cross-referencing resume with L1 interview performance."}
                                                </p>
                                                {analysis?.match_score && (
                                                    <div className="flex items-center gap-2 mt-2">
                                                        <div className="h-1 w-32 bg-gray-100 rounded-full overflow-hidden">
                                                            <div className="h-full bg-success transition-all duration-1000" style={{ width: `${analysis.match_score}%` }}></div>
                                                        </div>
                                                        <span className="text-[10px] font-black text-success uppercase tracking-widest">{analysis.match_score}% JD Match</span>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <button 
                                            onClick={handleDownloadReport}
                                            className="p-3 bg-white border border-border-subtle text-primary-blue rounded-xl hover:bg-bg-muted transition-all active:scale-95 flex items-center gap-2 text-xs font-bold uppercase tracking-widest shadow-sm"
                                        >
                                            <Download size={18} />
                                            Export PDF
                                        </button>
                                        <button className="px-6 py-3 bg-primary-dark text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-black transition-all active:scale-95 shadow-xl shadow-gray-200">
                                            Schedule Next Round
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* View Content */}
                            {intelligenceMode === 'recruiter' ? (
                                <div className="flex flex-col gap-6 animate-in slide-in-from-bottom-4 duration-500">
                                    {/* Standard Recruiter View */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-white p-8 rounded-[2rem] border border-border-subtle shadow-sm flex flex-col gap-6">
                                            <div className="flex items-center gap-3 text-red-600">
                                                <ShieldAlert size={24} />
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em]">Risk Analysis</h3>
                                            </div>
                                            <div className="flex flex-col gap-3">
                                                {analysis?.risk_analysis?.map((risk, i) => (
                                                    <div key={i} className="flex gap-3 p-4 bg-red-50/50 rounded-2xl border border-red-50">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0"></div>
                                                        <p className="text-sm text-red-900 font-medium">{risk}</p>
                                                    </div>
                                                ))}
                                                {analysis?.missing_skills?.map((skill, i) => (
                                                    <div key={`miss-${i}`} className="flex gap-3 p-4 bg-orange-50/50 rounded-2xl border border-orange-50">
                                                        <AlertTriangle size={14} className="text-orange-500 mt-1 shrink-0" />
                                                        <p className="text-sm text-orange-900 font-medium">Missing: {skill}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="bg-white p-8 rounded-[2rem] border border-border-subtle shadow-sm flex flex-col gap-6">
                                            <div className="flex items-center gap-3 text-success-text">
                                                <CheckCircle2 size={24} />
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em]">Core Strengths</h3>
                                            </div>
                                            <div className="flex flex-col gap-3">
                                                {analysis?.strengths?.map((strength, i) => (
                                                    <div key={i} className="flex gap-3 p-4 bg-success/5 rounded-2xl border border-success/10">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-success mt-1.5 shrink-0"></div>
                                                        <p className="text-sm text-success-text font-medium">{strength}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Questions Checklist */}
                                    <div className="bg-white p-8 rounded-[3rem] border border-border-subtle shadow-sm">
                                        <div className="flex items-center justify-between mb-8">
                                            <div className="flex items-center gap-3 text-primary-blue">
                                                <MessageSquareQuote size={24} />
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em]">Technical Screening Sheet</h3>
                                            </div>
                                            <div className="px-4 py-2 bg-primary-blue/10 text-primary-blue rounded-full text-[10px] font-black uppercase tracking-widest">
                                                {Object.values(checkedQuestions).filter(Boolean).length} / 10 Success
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-1 gap-4">
                                            {analysis?.initial_call_questions?.map((q, i) => (
                                                <div 
                                                    key={i} 
                                                    onClick={() => toggleQuestion(i)}
                                                    className={`flex gap-6 p-6 rounded-[2rem] border transition-all cursor-pointer group ${checkedQuestions[i] ? 'bg-success/5 border-success/30' : 'bg-bg-muted/50 border-gray-100'}`}
                                                >
                                                    <div className="shrink-0 pt-1">{checkedQuestions[i] ? <CheckSquare className="text-success" size={24} /> : <Square className="text-gray-300" size={24} />}</div>
                                                    <div className="flex-1 space-y-4">
                                                        <p className="text-sm text-primary-dark font-black leading-relaxed">{q.question}</p>
                                                        <div className="bg-white/60 p-5 rounded-[1.5rem] border border-dashed border-primary-blue/20">
                                                            <span className="text-[10px] font-black text-primary-blue uppercase tracking-widest block mb-2">HR Cheat Sheet</span>
                                                            <p className="text-xs text-text-muted italic">{q.expected_answer}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col gap-6 animate-in slide-in-from-bottom-4 duration-500">
                                    {managerAnalysis ? (
                                        <>
                                            {/* Managerial Analysis Display */}
                                            {/* Scores & Assessments Section */}
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                                <div className="bg-white p-8 rounded-[2.5rem] border border-border-subtle shadow-sm flex flex-col justify-between">
                                                    <div className="flex items-center gap-3 text-primary-blue mb-4">
                                                        <Trophy size={24} />
                                                        <h3 className="text-sm font-black uppercase tracking-[0.2em]">Written Test Score</h3>
                                                    </div>
                                                    <div className="flex items-baseline gap-2">
                                                        <span className="text-6xl font-black text-primary-dark">{managerAnalysis.written_test_score || 'N/A'}</span>
                                                        <span className="text-xs font-bold text-text-muted uppercase tracking-widest">Verified Result</span>
                                                    </div>
                                                    <p className="text-xs text-text-muted mt-4 font-medium italic">{managerAnalysis.written_test_analysis}</p>
                                                </div>

                                                <div className="md:col-span-2 bg-white p-8 rounded-[2.5rem] border border-border-subtle shadow-sm flex flex-col">
                                                    <div className="flex items-center gap-3 text-primary-blue mb-6">
                                                        <FileCheck size={24} />
                                                        <h3 className="text-sm font-black uppercase tracking-[0.2em]">Assessment Documents</h3>
                                                    </div>
                                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
                                                        {managerAnalysis.written_test_url && (
                                                            <a 
                                                                href={managerAnalysis.written_test_url} 
                                                                target="_blank" 
                                                                rel="noopener noreferrer"
                                                                className="flex items-center justify-between p-5 bg-bg-muted rounded-2xl hover:bg-primary-blue/5 border border-transparent hover:border-primary-blue/20 transition-all group"
                                                            >
                                                                <div className="flex items-center gap-4">
                                                                    <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                                                                        <FileText size={20} className="text-primary-blue" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-xs font-black text-primary-dark uppercase tracking-wider">Written Test</p>
                                                                        <p className="text-[10px] text-text-muted font-medium">Download PDF</p>
                                                                    </div>
                                                                </div>
                                                                <Download size={18} className="text-text-muted group-hover:text-primary-blue" />
                                                            </a>
                                                        )}

                                                        {managerAnalysis.transcript_url && (
                                                            <a 
                                                                href={managerAnalysis.transcript_url} 
                                                                target="_blank" 
                                                                rel="noopener noreferrer"
                                                                className="flex items-center justify-between p-5 bg-bg-muted rounded-2xl hover:bg-primary-blue/5 border border-transparent hover:border-primary-blue/20 transition-all group"
                                                            >
                                                                <div className="flex items-center gap-4">
                                                                    <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                                                                        <MessageSquareQuote size={20} className="text-primary-blue" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-xs font-black text-primary-dark uppercase tracking-wider">L1 Transcript</p>
                                                                        <p className="text-[10px] text-text-muted font-medium">View Conversation</p>
                                                                    </div>
                                                                </div>
                                                                <Download size={18} className="text-text-muted group-hover:text-primary-blue" />
                                                            </a>
                                                        )}
                                                        
                                                        {managerAnalysis.feedback_url && (
                                                            <a 
                                                                href={managerAnalysis.feedback_url} 
                                                                target="_blank" 
                                                                rel="noopener noreferrer"
                                                                className="flex items-center justify-between p-5 bg-bg-muted rounded-2xl hover:bg-primary-blue/5 border border-transparent hover:border-primary-blue/20 transition-all group"
                                                            >
                                                                <div className="flex items-center gap-4">
                                                                    <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                                                                        <CheckCircle2 size={20} className="text-success" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-xs font-black text-primary-dark uppercase tracking-wider">L1 Feedback</p>
                                                                        <p className="text-[10px] text-text-muted font-medium">Evaluation Form</p>
                                                                    </div>
                                                                </div>
                                                                <Download size={18} className="text-text-muted group-hover:text-primary-blue" />
                                                            </a>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="bg-[#0A0F1E] text-white p-10 rounded-[3rem] shadow-2xl relative overflow-hidden">
                                                <div className="absolute top-0 right-0 p-10 opacity-10">
                                                    <Zap size={120} />
                                                </div>
                                                <div className="relative z-10 max-w-3xl">
                                                    <h3 className="text-xs font-black uppercase tracking-[0.3em] text-primary-blue mb-4">Executive L1 Audit</h3>
                                                    <h4 className="text-2xl font-bold leading-relaxed mb-6">{managerAnalysis.l1_summary}</h4>
                                                    <div className="flex gap-4">
                                                        <div className="px-4 py-2 bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest">
                                                            Transcript Analyzed
                                                        </div>
                                                        <div className="px-4 py-2 bg-primary-blue/20 text-primary-blue rounded-xl text-[10px] font-black uppercase tracking-widest">
                                                            Resume Cross-Referenced
                                                        </div>
                                                        {managerAnalysis.written_test_score && (
                                                            <div className="px-4 py-2 bg-success/20 text-success rounded-xl text-[10px] font-black uppercase tracking-widest">
                                                                Written Test Verified
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                                {/* The Gap */}
                                                <div className="md:col-span-2 bg-white p-8 rounded-[2.5rem] border border-border-subtle shadow-sm">
                                                    <div className="flex items-center gap-3 text-orange-600 mb-6">
                                                        <AlertTriangle size={24} />
                                                        <h3 className="text-sm font-black uppercase tracking-[0.2em]">The Gap (Resume vs Interview)</h3>
                                                    </div>
                                                    <div className="space-y-4">
                                                        {managerAnalysis.the_gap.map((item, i) => (
                                                            <div key={i} className="p-5 bg-orange-50/50 rounded-2xl border border-orange-100 flex gap-4">
                                                                <div className="w-2 h-2 rounded-full bg-orange-400 mt-1.5 shrink-0"></div>
                                                                <p className="text-sm text-orange-900 font-medium">{item}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>

                                                {/* Pain Points */}
                                                <div className="bg-white p-8 rounded-[2.5rem] border border-border-subtle shadow-sm">
                                                    <div className="flex items-center gap-3 text-red-600 mb-6">
                                                        <Zap size={24} />
                                                        <h3 className="text-sm font-black uppercase tracking-[0.2em]">Pain Points</h3>
                                                    </div>
                                                    <div className="space-y-4">
                                                        {managerAnalysis.pain_points.map((item, i) => (
                                                            <div key={i} className="flex gap-3 text-red-900">
                                                                <AlertTriangle size={14} className="shrink-0 mt-1 opacity-50" />
                                                                <p className="text-sm font-bold italic">{item}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Managerial Strategy */}
                                            <div className="bg-white p-10 rounded-[3rem] border border-border-subtle shadow-sm">
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em] mb-8 text-primary-blue">Recommended Drill-Down Strategy (L2)</h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                    {managerAnalysis.manager_strategy.map((item, i) => (
                                                        <div key={i} className="p-8 bg-bg-muted/50 rounded-[2rem] border border-gray-100 hover:border-primary-blue/30 transition-all group">
                                                            <div className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-2 group-hover:text-primary-blue transition-colors">{item.topic}</div>
                                                            <p className="text-base font-black text-primary-dark mb-4 leading-relaxed underline decoration-primary-blue/30 underline-offset-4">{item.drill_down_question}</p>
                                                            <div className="flex gap-3 items-start">
                                                                <div className="w-1 h-1 bg-primary-blue mt-1.5 rounded-full shrink-0"></div>
                                                                <p className="text-xs text-text-muted font-medium italic">{item.why}</p>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="p-20 text-center flex flex-col items-center gap-4">
                                            <Loader2 className="animate-spin text-primary-blue" size={40} />
                                            <p className="text-sm font-bold text-text-muted uppercase tracking-widest">Cross-Referencing Intelligence...</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CandidatesPage;
