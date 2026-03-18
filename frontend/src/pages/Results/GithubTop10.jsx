import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScreening } from '../../context/ScreeningContext';
import { 
  ArrowLeft, 
  Github, 
  Code, 
  Trophy, 
  ChevronRight, 
  Star, 
  Layout, 
  Zap, 
  CheckCircle,
  ExternalLink
} from 'lucide-react';

const GithubTop10 = () => {
    const { results, setSelectedCandidateId } = useScreening();
    const navigate = useNavigate();

    const top10Candidates = useMemo(() => {
        if (!results || !results.ranking || !results.evaluations) return [];

        const candidatesWithScores = results.ranking.map(cand => {
            const evalData = results.evaluations[cand.candidate_id];
            const rubric = evalData?.github_rubric || evalData?.github_features?.rubric_scores || {};
            
            // Calculate overall GitHub score out of 100
            const codeQuality = rubric.code_quality || 0;
            const jdRelevance = rubric.jd_relevance || 0;
            const complexity = rubric.complexity || 0;
            const bestPractices = rubric.best_practices || 0;
            
            const overallScore = codeQuality + jdRelevance + complexity + bestPractices;
            
            return {
                ...cand,
                rubric,
                overallGithubScore: overallScore,
                hasGithubData: (evalData?.github_score || 0) > 0
            };
        });

        return candidatesWithScores
            .filter(c => c.hasGithubData)
            .sort((a, b) => b.overallGithubScore - a.overallGithubScore)
            .slice(0, 10);
    }, [results]);

    if (!results) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-50">
                <div className="animate-pulse flex flex-col items-center gap-4">
                    <Github className="text-gray-300 w-12 h-12" />
                    <p className="text-gray-400 font-bold uppercase tracking-widest text-xs">Loading Intelligence...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 bg-gray-50/50 p-6 md:p-10 overflow-y-auto w-full h-full">
            <div className="max-w-6xl mx-auto flex flex-col gap-8">
                
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div className="flex flex-col gap-4">
                        <button
                            onClick={() => navigate('/results')}
                            className="flex items-center gap-2 text-sm font-black uppercase tracking-widest text-gray-400 hover:text-primary-blue transition-colors group w-max"
                        >
                            <ArrowLeft size={16} />
                            Back to Pipeline
                        </button>
                        <div className="flex items-center gap-4">
                            <div className="p-4 bg-black text-white rounded-[1.5rem] shadow-xl shadow-black/10">
                                <Trophy size={32} />
                            </div>
                            <div className="flex flex-col">
                                <h1 className="text-4xl font-black text-[#1A1A1A] tracking-tight">GitHub Elite Top 10</h1>
                                <p className="text-gray-500 font-medium">Top engineering talent ranked by multi-dimensional rubric analysis.</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Top 10 List */}
                <div className="grid grid-cols-1 gap-4">
                    {top10Candidates.length > 0 ? (
                        top10Candidates.map((cand, idx) => (
                            <div 
                                key={cand.candidate_id}
                                className="group bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-xl hover:shadow-blue-500/5 transition-all duration-500 overflow-hidden cursor-pointer"
                                onClick={() => {
                                    setSelectedCandidateId(cand.candidate_id);
                                    navigate('/results');
                                }}
                            >
                                <div className="p-6 md:p-8 flex flex-col md:flex-row items-center gap-8">
                                    {/* Rank & Badge */}
                                    <div className="flex items-center gap-6">
                                        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-black ${
                                            idx === 0 ? 'bg-yellow-400 text-yellow-900 shadow-lg shadow-yellow-200' :
                                            idx === 1 ? 'bg-gray-200 text-gray-600 shadow-lg shadow-gray-100' :
                                            idx === 2 ? 'bg-orange-200 text-orange-700 shadow-lg shadow-orange-100' :
                                            'bg-blue-50 text-primary-blue border border-blue-100'
                                        }`}>
                                            #{idx + 1}
                                        </div>
                                        <div className="flex flex-col min-w-[200px]">
                                            <h3 className="text-xl font-black text-[#1A1A1A] group-hover:text-primary-blue transition-colors">{cand.name}</h3>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">ID: {cand.candidate_id}</span>
                                                <span className="px-2 py-0.5 bg-gray-50 text-gray-400 text-[8px] font-black uppercase rounded">Global Rank #{cand.rank}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Overall Score Circle */}
                                    <div className="flex flex-col items-center gap-1 md:border-l md:border-r border-gray-100 px-10">
                                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Overall GitHub Score</span>
                                        <div className="relative flex items-center justify-center">
                                            <svg className="w-16 h-16 transform -rotate-90">
                                                <circle
                                                    cx="32"
                                                    cy="32"
                                                    radius="28"
                                                    stroke="currentColor"
                                                    strokeWidth="6"
                                                    fill="transparent"
                                                    className="text-gray-100"
                                                    r="28"
                                                />
                                                <circle
                                                    cx="32"
                                                    cy="32"
                                                    radius="28"
                                                    stroke="currentColor"
                                                    strokeWidth="6"
                                                    strokeDasharray={2 * Math.PI * 28}
                                                    strokeDashoffset={2 * Math.PI * 28 * (1 - cand.overallGithubScore / 100)}
                                                    fill="transparent"
                                                    className="text-primary-blue transition-all duration-1000 ease-out"
                                                    r="28"
                                                />
                                            </svg>
                                            <span className="absolute text-lg font-black text-primary-blue">{cand.overallGithubScore}</span>
                                        </div>
                                    </div>

                                    {/* Rubric Breakdown */}
                                    <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
                                        {[
                                            { label: 'Code Quality', val: cand.rubric.code_quality, icon: Code },
                                            { label: 'JD Relevance', val: cand.rubric.jd_relevance, icon: Zap },
                                            { label: 'Complexity', val: cand.rubric.complexity, icon: Layout },
                                            { label: 'Best Practices', val: cand.rubric.best_practices, icon: CheckCircle },
                                        ].map((item, i) => (
                                            <div key={i} className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1.5 text-gray-400">
                                                    <item.icon size={12} />
                                                    <span className="text-[9px] font-black uppercase tracking-wider">{item.label}</span>
                                                </div>
                                                <div className="text-sm font-black text-[#1A1A1A]">{item.val || 0}/25</div>
                                                <div className="w-full h-1 bg-gray-50 rounded-full overflow-hidden">
                                                    <div 
                                                        className="h-full bg-blue-400 rounded-full"
                                                        style={{ width: `${((item.val || 0) / 25) * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Action */}
                                    <div className="hidden md:flex items-center">
                                        <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center text-gray-300 group-hover:bg-primary-blue group-hover:text-white transition-all transform group-hover:translate-x-1">
                                            <ChevronRight size={20} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="flex flex-col items-center justify-center p-20 bg-white rounded-[2.5rem] border border-dashed border-gray-200">
                            <Github size={48} className="text-gray-200 mb-4" />
                            <p className="text-gray-400 font-bold uppercase tracking-widest text-sm text-center">
                                No GitHub evaluations available yet.<br/>
                                <span className="text-[10px] font-medium opacity-70">Please run Stage 2 GitHub Verification first.</span>
                            </p>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default GithubTop10;
