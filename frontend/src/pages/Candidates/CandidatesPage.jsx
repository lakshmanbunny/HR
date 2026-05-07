import React, { useState, useEffect } from 'react';
import { Search, User, FileText, AlertTriangle, CheckCircle2, ShieldAlert, Zap, Loader2, ChevronRight, MessageSquareQuote, Upload, Download, CheckSquare, Square } from 'lucide-react';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const CandidatesPage = () => {
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCandidate, setSelectedCandidate] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [analyzingId, setAnalyzingId] = useState(null);
    const [isDirectUpload, setIsDirectUpload] = useState(false);
    
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
        setCheckedQuestions({});
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

    const handleDirectUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsDirectUpload(true);
        setSelectedCandidate({ name: file.name.split('.')[0], id: 'GUEST' });
        setAnalyzingId('DIRECT');
        setAnalysis(null);
        setCheckedQuestions({});

        const formData = new FormData();
        formData.append('file', file);

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
        }
    };

    const toggleQuestion = (index) => {
        setCheckedQuestions(prev => ({
            ...prev,
            [index]: !prev[index]
        }));
    };

    const handleDownloadReport = () => {
        if (!analysis) return;

        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        
        // Header
        doc.setFillColor(10, 15, 30); // Primary Dark
        doc.rect(0, 0, pageWidth, 40, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont('helvetica', 'bold');
        doc.text("Technical Interview Sheet", 20, 25);
        
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(`Candidate: ${selectedCandidate?.name || 'Unknown'}`, 20, 33);
        doc.text(`Date: ${new Date().toLocaleDateString()}`, pageWidth - 60, 33);

        // Score Summary
        const successCount = Object.values(checkedQuestions).filter(Boolean).length;
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(12);
        doc.text(`Candidate Performance Score: ${successCount} / 10`, 20, 55);
        
        // Table Data
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
            headStyles: { fillColor: [0, 102, 255], textColor: 255, fontStyle: 'bold' },
            columnStyles: {
                0: { cellWidth: 10 },
                1: { cellWidth: 20, fontStyle: 'bold' },
                2: { cellWidth: 'auto' }
            },
            alternateRowStyles: { fillColor: [245, 247, 250] },
            margin: { top: 60 }
        });

        // Risk & Strength summary footer
        const finalY = doc.lastAutoTable.finalY + 20;
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text("AI Profile Risks", 20, finalY);
        
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');
        analysis.risk_analysis.slice(0, 3).forEach((risk, i) => {
            doc.text(`• ${risk}`, 25, finalY + 10 + (i * 6));
        });

        doc.save(`Interview_Sheet_${selectedCandidate?.name.replace(/\s+/g, '_') || 'Candidate'}.pdf`);
    };

    const filteredCandidates = candidates.filter(c => 
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        (c.skills && c.skills.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="flex flex-col gap-8 pb-10">
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
                    
                    <label className="shrink-0 cursor-pointer group">
                        <div className="flex items-center gap-2 px-6 py-3.5 bg-primary-blue text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-primary-dark transition-all active:scale-95 shadow-xl shadow-blue-100">
                            <Upload size={16} />
                            New AI Audit
                        </div>
                        <input type="file" accept=".pdf" className="hidden" onChange={handleDirectUpload} />
                    </label>
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
                            <div className="bg-white p-8 rounded-[2rem] border border-border-subtle shadow-sm flex items-center justify-between">
                                <div className="flex items-center gap-6">
                                    <div className="w-16 h-16 bg-primary-blue rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-200">
                                        {isDirectUpload ? <FileText size={32} /> : <User size={32} />}
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-black text-[#0A0F1E] truncate max-w-[400px]">{selectedCandidate.name}</h2>
                                        <div className="flex items-center gap-4 mt-1">
                                            <span className="text-xs font-bold text-text-muted flex items-center gap-1.5">
                                                <CheckCircle2 size={14} className="text-success" /> {isDirectUpload ? 'External Upload' : 'OpenCATS Profile'}
                                            </span>
                                            <span className="text-xs font-bold text-success-text flex items-center gap-1.5 px-2 py-0.5 bg-success/10 rounded-full">
                                                <Zap size={10} /> Gemini 2.0 Flash Verified
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    {analysis && (
                                        <button 
                                            onClick={handleDownloadReport}
                                            className="p-3 bg-primary-blue text-white rounded-xl hover:bg-primary-dark transition-all active:scale-95 flex items-center gap-2 text-xs font-bold uppercase tracking-widest shadow-lg shadow-blue-100"
                                        >
                                            <Download size={18} />
                                            Download PDF
                                        </button>
                                    )}
                                    <button className="px-6 py-3 bg-primary-dark text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-black transition-all active:scale-95 shadow-xl shadow-gray-200">
                                        Schedule Interview
                                    </button>
                                </div>
                            </div>

                            {analysis?.error ? (
                                <div className="bg-white p-12 rounded-[2.5rem] border border-dashed border-red-200 flex flex-col items-center text-center gap-8 shadow-xl shadow-red-50 relative overflow-hidden">
                                    <div className="absolute top-0 left-0 w-full h-1 bg-red-100"></div>
                                    <div className="w-20 h-20 bg-red-50 rounded-[2rem] flex items-center justify-center text-red-500">
                                        <AlertTriangle size={40} />
                                    </div>
                                    <div className="max-w-md">
                                        <h3 className="text-xl font-black text-red-900 uppercase tracking-widest">Analysis Failure</h3>
                                        <p className="text-sm text-red-700/70 mt-3 font-medium leading-relaxed italic">{analysis.error}</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col gap-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {/* Risks */}
                                        <div className="bg-white p-8 rounded-[2rem] border border-border-subtle shadow-sm flex flex-col gap-6">
                                            <div className="flex items-center gap-3 text-red-600">
                                                <ShieldAlert size={24} />
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em]">Risk Analysis</h3>
                                            </div>
                                            <div className="flex flex-col gap-3">
                                                {analysis?.risk_analysis?.map((risk, i) => (
                                                    <div key={i} className="flex gap-3 p-4 bg-red-50/50 rounded-2xl border border-red-50">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0"></div>
                                                        <p className="text-sm text-red-900 font-medium leading-relaxed">{risk}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Strengths */}
                                        <div className="bg-white p-8 rounded-[2rem] border border-border-subtle shadow-sm flex flex-col gap-6">
                                            <div className="flex items-center gap-3 text-success-text">
                                                <CheckCircle2 size={24} />
                                                <h3 className="text-sm font-black uppercase tracking-[0.2em]">Core Strengths</h3>
                                            </div>
                                            <div className="flex flex-col gap-3">
                                                {analysis?.strengths?.map((strength, i) => (
                                                    <div key={i} className="flex gap-3 p-4 bg-success/5 rounded-2xl border border-success/10">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-success mt-1.5 shrink-0"></div>
                                                        <p className="text-sm text-success-text font-medium leading-relaxed">{strength}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Questions Section */}
                                    <div className="bg-white p-8 rounded-[3rem] border border-border-subtle shadow-sm flex flex-col gap-8">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3 text-primary-blue">
                                                <MessageSquareQuote size={24} />
                                                <div>
                                                    <h3 className="text-sm font-black uppercase tracking-[0.2em]">Technical Interview Verification</h3>
                                                    <p className="text-[10px] text-text-muted font-bold mt-1 uppercase tracking-widest">10 Project-Specific Questions with HR Guide</p>
                                                </div>
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
                                                    className={`flex gap-6 p-6 rounded-[2rem] border transition-all cursor-pointer group ${checkedQuestions[i] ? 'bg-success/5 border-success/30 shadow-lg shadow-success/5' : 'bg-bg-muted/50 border-gray-100 hover:border-primary-blue/30'}`}
                                                >
                                                    <div className="shrink-0 pt-1">
                                                        {checkedQuestions[i] ? (
                                                            <CheckSquare className="text-success animate-in zoom-in duration-300" size={24} />
                                                        ) : (
                                                            <Square className="text-gray-300 group-hover:text-primary-blue" size={24} />
                                                        )}
                                                    </div>
                                                    
                                                    <div className="flex-1 space-y-4">
                                                        <p className="text-sm text-primary-dark font-black leading-relaxed">
                                                            {typeof q === 'string' ? q : q.question}
                                                        </p>
                                                        
                                                        {q.expected_answer && (
                                                            <div className="bg-white/60 p-5 rounded-[1.5rem] border border-dashed border-primary-blue/20">
                                                                <span className="text-[10px] font-black text-primary-blue uppercase tracking-widest block mb-2 flex items-center gap-2">
                                                                    <Zap size={12} /> HR CHEAT SHEET (VERIFICATION GUIDE)
                                                                </span>
                                                                <p className="text-xs text-text-muted font-medium italic leading-relaxed">
                                                                    {q.expected_answer}
                                                                </p>
                                                            </div>
                                                        )}
                                                    </div>

                                                    <div className="shrink-0 text-2xl font-black text-gray-100 group-hover:text-primary-blue/10 transition-colors">
                                                        {String(i + 1).padStart(2, '0')}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
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
