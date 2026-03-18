import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Upload, FileText, ChevronLeft, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

const UploadPage = () => {
    const { type } = useParams();
    const navigate = useNavigate();
    const [resumeFile, setResumeFile] = useState(null);
    const [jdFile, setJdFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);

    const handleStartScreening = () => {
        setIsUploading(true);
        // Simulate start – in a real app, this would trigger the actual upload/pipeline
        setTimeout(() => {
            navigate('/processing');
        }, 1500);
    };

    return (
        <div className="flex-1 flex flex-col py-8 animate-in fade-in duration-500">
            {/* Header / Breadcrumb */}
            <div className="flex items-center gap-4 mb-10">
                <button 
                    onClick={() => navigate('/')}
                    className="p-3 bg-white border border-border-subtle rounded-2xl text-text-muted hover:text-primary-blue hover:border-primary-blue transition-all active:scale-95 shadow-sm"
                >
                    <ChevronLeft size={20} />
                </button>
                <div>
                    <h1 className="text-2xl font-black text-[#0A0F1E] tracking-tight">
                        Pipeline Setup: <span className="text-primary-blue capitalize">{type}</span>
                    </h1>
                    <p className="text-xs text-text-muted font-bold uppercase tracking-[0.2em] mt-1">Grounding Intelligence Layer</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl">
                {/* Resume Upload Section */}
                <div className={`p-10 rounded-[2.5rem] border-2 transition-all flex flex-col items-center justify-center text-center gap-6 group relative overflow-hidden h-[400px] ${resumeFile ? 'bg-success/5 border-success/20' : 'bg-white border-dashed border-gray-200 hover:border-primary-blue/30'}`}>
                    {resumeFile ? (
                        <>
                            <div className="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center text-success animate-in zoom-in duration-300">
                                <CheckCircle2 size={40} />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-success-text">Resumes Received</h3>
                                <p className="text-sm text-success-text/70 mt-1 font-medium">{resumeFile.name || 'Batch Upload Active'}</p>
                            </div>
                            <button onClick={() => setResumeFile(null)} className="text-xs font-bold text-success-text/50 uppercase tracking-widest hover:text-red-500 transition-colors">Replace Files</button>
                        </>
                    ) : (
                        <>
                            <div className="w-20 h-20 bg-primary-blue/5 rounded-3xl flex items-center justify-center text-primary-blue group-hover:scale-110 transition-transform">
                                <Upload size={32} />
                            </div>
                            <div className="max-w-xs">
                                <h3 className="text-xl font-bold text-[#0A0F1E]">Upload Resumes</h3>
                                <p className="text-sm text-text-muted mt-2 font-medium leading-relaxed italic">
                                    Drop PDF, DOCX or ZIP files here to start intelligence extraction
                                </p>
                            </div>
                            <input 
                                type="file" 
                                className="absolute inset-0 opacity-0 cursor-pointer" 
                                onChange={(e) => setResumeFile({ name: e.target.files[0]?.name || 'files_selected' })} 
                            />
                        </>
                    )}
                </div>

                {/* JD Upload Section */}
                <div className={`p-10 rounded-[2.5rem] border-2 transition-all flex flex-col items-center justify-center text-center gap-6 group relative overflow-hidden h-[400px] ${jdFile ? 'bg-indigo-50 border-indigo-200' : 'bg-white border-dashed border-gray-200 hover:border-primary-blue/30'}`}>
                    {jdFile ? (
                        <>
                            <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 animate-in zoom-in duration-300">
                                <FileText size={40} />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-indigo-900">Job Description Locked</h3>
                                <p className="text-sm text-indigo-900/70 mt-1 font-medium">{jdFile.name || 'Project-X-JD.pdf'}</p>
                            </div>
                            <button onClick={() => setJdFile(null)} className="text-xs font-bold text-indigo-900/50 uppercase tracking-widest hover:text-red-500 transition-colors">Replace JD</button>
                        </>
                    ) : (
                        <>
                            <div className="w-20 h-20 bg-indigo-50 rounded-3xl flex items-center justify-center text-indigo-500 group-hover:scale-110 transition-transform">
                                <FileText size={32} />
                            </div>
                            <div className="max-w-xs">
                                <h3 className="text-xl font-bold text-[#0A0F1E]">Upload JD</h3>
                                <p className="text-sm text-text-muted mt-2 font-medium leading-relaxed italic">
                                    Provide the job criteria to ground the AI's screening logic
                                </p>
                            </div>
                            <input 
                                type="file" 
                                className="absolute inset-0 opacity-0 cursor-pointer" 
                                onChange={(e) => setJdFile({ name: e.target.files[0]?.name || 'jd_selected' })} 
                            />
                        </>
                    )}
                </div>
            </div>

            {/* Action Section */}
            <div className="mt-12 flex flex-col items-center gap-6">
                {!resumeFile || !jdFile ? (
                    <div className="flex items-center gap-2 px-6 py-3 bg-red-50 border border-red-100 rounded-2xl animate-in slide-in-from-bottom-2">
                        <AlertCircle size={16} className="text-red-500" />
                        <span className="text-[11px] font-black text-red-600 uppercase tracking-widest">
                            {(!resumeFile && !jdFile) ? "Resources Mandatory: Resumes & JD Required" : !resumeFile ? "Missing Field: Please Upload Resumes" : "Missing Field: Please Upload JD"}
                        </span>
                    </div>
                ) : (
                    <div className="flex items-center gap-2 px-6 py-3 bg-success/10 border border-success/20 rounded-2xl animate-in fade-in zoom-in">
                        <CheckCircle2 size={16} className="text-success" />
                        <span className="text-[11px] font-black text-success-text uppercase tracking-widest">System Ready • Target Environment Calibrated</span>
                    </div>
                )}

                <button 
                    disabled={!resumeFile || !jdFile || isUploading}
                    onClick={handleStartScreening}
                    className={`min-w-[320px] py-6 rounded-[2rem] font-black uppercase tracking-[0.2em] text-sm flex items-center justify-center gap-4 transition-all shadow-2xl ${
                        resumeFile && jdFile 
                        ? 'bg-primary-dark text-white hover:bg-black hover:shadow-primary-blue/30 active:scale-95' 
                        : 'bg-bg-muted text-text-muted cursor-not-allowed border border-border-subtle'
                    }`}
                >
                    {isUploading ? (
                        <>
                            <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                            <span>Initializing Pipeline...</span>
                        </>
                    ) : (
                        <>
                            <span>Run AI Agents</span>
                            <ArrowRight size={20} className="animate-pulse" />
                        </>
                    )}
                </button>

                <p className="text-[10px] text-text-muted font-bold uppercase tracking-[0.3em] max-w-sm text-center">
                    Gating active. Proceeding will consume compute tokens and initiate 3-stage intelligence funnel.
                </p>
            </div>
        </div>
    );
};

export default UploadPage;
