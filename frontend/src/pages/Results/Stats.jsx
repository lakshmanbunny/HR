import React, { useState, useEffect } from 'react';
import { TrendingUp, Clock, Users, CheckCircle, BarChart3, ArrowUpRight, Calendar, Filter, Briefcase, User as UserIcon, AlertCircle, Info } from 'lucide-react';
import RecruitmentFunnel from '../../components/RecruitmentFunnel';
import RecruitmentFunnelV2 from '../../components/RecruitmentFunnelV2';

const API_BASE = "/api";



const Stats = () => {
    const [statsData, setStatsData] = useState(null);
    const [funnelData, setFunnelData] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [recruiters, setRecruiters] = useState([]);
    
    const [activePlacements, setActivePlacements] = useState([]);
    const [showTracker, setShowTracker] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isFunnelLoading, setIsFunnelLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");
    
    const [filterDays, setFilterDays] = useState(30);
    const [selectedJob, setSelectedJob] = useState("");
    const [selectedRecruiter, setSelectedRecruiter] = useState("");
    const [selectedStatus, setSelectedStatus] = useState("");
    const [isPreviewMode, setIsPreviewMode] = useState(false);

    // Helper for fetch with timeout
    const fetchWithTimeout = async (url, options = {}, timeout = 5000) => {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);
        const response = await fetch(url, { ...options, signal: controller.signal });
        clearTimeout(id);
        return response;
    };

    // 1. Initial Load: Jobs & Recruiters (Always fetched)
    useEffect(() => {
        const fetchFilters = async () => {
            try {
                const [jobsRes, recruitersRes] = await Promise.all([
                    fetchWithTimeout(`${API_BASE}/jobs`),
                    fetchWithTimeout(`${API_BASE}/recruiters`)
                ]);
                
                if (jobsRes.ok) {
                    const jobsData = await jobsRes.json();
                    setJobs(Array.isArray(jobsData) ? jobsData : []);
                }
                if (recruitersRes.ok) {
                    const recruitersData = await recruitersRes.json();
                    setRecruiters(Array.isArray(recruitersData) ? recruitersData : []);
                }
            } catch (error) {
                console.error("Error fetching filters:", error);
            }
        };
        fetchFilters();
    }, []);

    // 2. Fetch Stats (Cards & Velocity) - ONLY affected by Date Filter
    useEffect(() => {
        const fetchStats = async () => {
            setIsLoading(true);
            setErrorMessage("");
        try {
                let url = `${API_BASE}/stats?days=${filterDays}`;
                if (selectedStatus) url += `&job_status=${selectedStatus}`;
                
                const response = await fetchWithTimeout(url);
                if (!response.ok) {
                    throw new Error(`Failed to fetch stats: ${response.status} ${response.statusText}`);
                }
                const data = await response.json();
                setStatsData(data);
                setIsPreviewMode(false);
            } catch (error) {
                console.error("Error fetching stats:", error);
                setErrorMessage("Database connectivity issue. Please check your connection.");
                setIsPreviewMode(true);
                setStatsData(null);
            } finally {
                setIsLoading(false);
            }
        };
        fetchStats();
    }, [filterDays, selectedStatus]);

    // 3. Fetch Funnel Data - Affected by ALL Filters
    useEffect(() => {
        const fetchFunnel = async () => {
            setIsFunnelLoading(true);
            try {
                let url = `${API_BASE}/funnel?days=${filterDays}`;
                if (selectedJob) url += `&joborder_id=${selectedJob}`;
                if (selectedRecruiter) url += `&recruiter_id=${selectedRecruiter}`;
                if (selectedStatus) url += `&job_status=${selectedStatus}`;
                
                const response = await fetchWithTimeout(url);
                if (response.ok) {
                    const data = await response.json();
                    setFunnelData(Array.isArray(data) ? data : []);
                } else {
                    setFunnelData([]);
                }
            } catch (error) {
                console.error("Error fetching funnel stats:", error);
                setFunnelData([]);
            } finally {
                setIsFunnelLoading(false);
            }
        };
        fetchFunnel();
    }, [filterDays, selectedJob, selectedRecruiter, selectedStatus]);

    const handleShowTracker = async () => {
        if (!showTracker) {
            try {
                const response = await fetchWithTimeout(`${API_BASE}/placements/active`);
                if (response.ok) {
                    const data = await response.json();
                    setActivePlacements(Array.isArray(data) ? data : []);
                }
            } catch (error) {
                console.error("Error fetching active placements:", error);
            }
        }
        setShowTracker(!showTracker);
    };

    // Prepare metrics from real data or fallbacks
    const metrics = statsData ? [
        {
            title: "Average Time to Fill",
            value: `${statsData.avg_time_to_fill || 0} Days`,
            change: "-2.4%", trend: "down", icon: Clock,
            color: "text-primary-blue", bg: "bg-primary-blue/10"
        },
        {
            title: "Average Time to Offer",
            value: `${statsData.avg_time_to_offer || 0} Days`,
            change: "Velocity", trend: "up", icon: Clock,
            color: "text-indigo-600", bg: "bg-indigo-50"
        },
        {
            title: "Total Active Openings",
            value: (statsData.total_active_openings || 0).toLocaleString(),
            change: "Live", trend: "up", icon: BarChart3,
            color: "text-purple-600", bg: "bg-purple-50"
        },
        {
            title: "Offer-to-Onboard Ratio",
            value: `${statsData.offer_to_onboarding_ratio || 0}%`,
            change: `Past: ${statsData.offer_breakdown?.past_offers || 0} / Future: ${statsData.offer_breakdown?.future_offers || 0}`, 
            trend: "up", icon: Award,
            color: "text-success", bg: "bg-success/10",
            tooltip: "Ratio of Joined candidates vs Offers made for past joining dates."
        },
        {
            title: "Enrolled Candidates",
            value: (statsData.total_considered_candidates || 0).toLocaleString(),
            change: "Active", trend: "up", icon: Users,
            color: "text-orange-500", bg: "bg-orange-50"
        }
    ] : [];

    // Only show full loading if we have absolutely no data yet
    if (isLoading && !statsData) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-primary-blue border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-sm font-bold text-primary-blue uppercase tracking-widest animate-pulse">Initial Syncing...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-10 pb-20 relative">
            {/* Active Placement Tracker Modal Overlay */}
            {showTracker && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-white w-full max-w-4xl max-h-[80vh] rounded-3xl overflow-hidden shadow-2xl flex flex-col">
                        <div className="p-8 border-b border-border-subtle flex items-center justify-between bg-[#0A0F1E] text-white">
                            <div>
                                <h3 className="text-xl font-black tracking-tight">Active Placement Tracker</h3>
                                <p className="text-xs text-white/60 font-medium">Real-time status of candidates in the Interviewing pipeline</p>
                            </div>
                            <button onClick={() => setShowTracker(false)} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                                <Users size={24} />
                            </button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-8">
                            <table className="w-full text-left">
                                <thead>
                                    <tr className="border-b border-border-subtle">
                                        <th className="pb-4 text-[11px] font-black text-text-muted uppercase tracking-widest">Candidate</th>
                                        <th className="pb-4 text-[11px] font-black text-text-muted uppercase tracking-widest">Applied Job</th>
                                        <th className="pb-4 text-[11px] font-black text-text-muted uppercase tracking-widest text-center">Days at Stage</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border-subtle">
                                    {(activePlacements || []).map((p, i) => (
                                        <tr key={i} className="hover:bg-bg-muted transition-colors group">
                                            <td className="py-4 text-sm font-bold text-text-main group-hover:text-primary-blue">{p.name || "Unknown"}</td>
                                            <td className="py-4 text-sm text-text-muted">{p.job || "No Title"}</td>
                                            <td className="py-4 text-sm font-black text-primary-dark text-center">
                                                <span className="px-3 py-1 bg-primary-blue/10 text-primary-blue rounded-full">{p.days || 0} Days</span>
                                            </td>
                                        </tr>
                                    ))}
                                    {(!activePlacements || activePlacements.length === 0) && (
                                        <tr><td colSpan="3" className="py-10 text-center text-sm text-text-muted font-bold">No active candidates in Interviewing status.</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* Status Alert for Preview Mode */}
            {isPreviewMode && (
                <div className="bg-amber-50 border border-amber-100 p-4 rounded-2xl flex items-center gap-4 animate-in fade-in slide-in-from-top duration-500">
                    <div className="p-2 bg-amber-100 text-amber-600 rounded-xl">
                        <AlertCircle size={20} />
                    </div>
                    <div>
                        <p className="text-sm font-black text-amber-900 uppercase tracking-widest">Database Offline (Home Mode)</p>
                        <p className="text-xs text-amber-700 font-medium">Showing illustrative data models. Real-time recruitment metrics will sync once you connect to the ParadigmIT network.</p>
                    </div>
                </div>
            )}

            {/* Header Section */}
            <section>
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-black text-[#0A0F1E] tracking-tight mb-3">Recruitment Intelligence <span className="text-primary-blue">Statistics</span></h1>
                        <p className="text-sm text-text-muted max-w-2xl font-medium leading-relaxed">
                            Deep-dive metrics and performance analytics for your hiring funnel. Track efficiency from position opening to onboarding.
                        </p>
                    </div>
                    
                    {/* Multi-Level Filtering Bar */}
                    <div className="flex flex-wrap items-center gap-3 p-3 bg-white border border-border-subtle rounded-2xl shadow-sm">
                        {/* Global Filter */}
                        <div className="flex items-center gap-2 px-3 py-1.5 border-r border-border-subtle group" title="Applies to ALL metrics">
                           <Calendar size={14} className="text-primary-blue" />
                           <select 
                                value={filterDays} 
                                onChange={(e) => setFilterDays(parseInt(e.target.value))}
                                className="text-[10px] font-black text-text-main uppercase tracking-wider bg-transparent border-none outline-none cursor-pointer"
                            >
                                <option value="30">Last Month</option>
                                <option value="90">Last Quarter</option>
                                <option value="365">Last Year</option>
                                <option value="10000">Overall</option>
                            </select>
                        </div>

                        {/* Scoped Filters (Funnel Only) */}
                        <div className="flex items-center gap-2 px-3 py-1.5 border-r border-border-subtle bg-bg-muted/30 rounded-lg" title="Applies to FUNNEL only">
                           <Briefcase size={14} className="text-purple-600" />
                           <select 
                                value={selectedJob} 
                                onChange={(e) => setSelectedJob(e.target.value)}
                                className="text-[10px] font-black text-text-main uppercase tracking-wider bg-transparent border-none outline-none cursor-pointer max-w-[150px]"
                            >
                                <option value="">Global Jobs</option>
                                {(jobs || []).map(j => (
                                    <option key={j.id} value={j.id}>{j.title}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex items-center gap-2 px-3 py-1.5 border-r border-border-subtle bg-bg-muted/30 rounded-lg" title="Applies to FUNNEL only">
                           <UserIcon size={14} className="text-orange-500" />
                           <select 
                                value={selectedRecruiter} 
                                onChange={(e) => setSelectedRecruiter(e.target.value)}
                                className="text-[10px] font-black text-text-main uppercase tracking-wider bg-transparent border-none outline-none cursor-pointer max-w-[150px]"
                            >
                                <option value="">Global Recruiters</option>
                                {(recruiters || []).map(r => (
                                    <option key={r.id} value={r.id}>{r.name}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex items-center gap-2 px-3 py-1.5 bg-bg-muted/30 rounded-lg" title="Job Status Filter">
                           <Filter size={14} className="text-blue-500" />
                           <select 
                                value={selectedStatus} 
                                onChange={(e) => setSelectedStatus(e.target.value)}
                                className="text-[10px] font-black text-text-main uppercase tracking-wider bg-transparent border-none outline-none cursor-pointer w-[100px]"
                            >
                                <option value="">All Statuses</option>
                                <option value="Active">Active</option>
                                <option value="Closed">Closed</option>
                                <option value="On Hold">On Hold</option>
                                <option value="Full">Full</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {metrics.map((metric, idx) => (
                        <div key={idx} className="bg-white p-6 rounded-2xl border border-border-subtle shadow-soft transition-all hover:shadow-lg hover:-translate-y-1 group">
                            <div className="flex items-start justify-between mb-4">
                                <div className={`p-3 rounded-xl ${metric.bg} ${metric.color}`}>
                                    <metric.icon size={24} />
                                </div>
                                <div className={`flex items-center gap-1 font-bold text-[10px] uppercase tracking-wider ${metric.trend === 'up' ? 'text-success' : 'text-primary-blue'}`}>
                                    {metric.change}
                                    <ArrowUpRight size={12} className={metric.trend === 'down' ? 'rotate-90' : ''} />
                                </div>
                            </div>
                            <h3 className="text-[11px] font-black text-text-muted uppercase tracking-[0.2em] mb-1">{metric.title}</h3>
                            <p className="text-2xl font-black text-[#0A0F1E]">{metric.value}</p>
                            {metric.tooltip && <p className="text-[9px] text-text-muted font-medium mt-2 leading-tight">{metric.tooltip}</p>}
                        </div>
                    ))}
                </div>
            </section>

            {/* Main Recruitment Funnel - V-Shape Version */}
            <section className="space-y-8">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Users size={18} className="text-primary-blue" />
                        <h4 className="text-sm font-black text-text-muted uppercase tracking-widest">Recruitment Funnel Analysis (V-Shape)</h4>
                    </div>
                </div>
                
                <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
                    <div className="xl:col-span-3">
                        <RecruitmentFunnelV2 data={funnelData} loading={isFunnelLoading} />
                    </div>
                    
                    {/* Integrated Analytics Card */}
                    <div className="bg-[#0A0F1E] rounded-3xl p-8 text-white flex flex-col justify-between relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-blue/20 rounded-full blur-[80px] -mr-32 -mt-32 group-hover:bg-primary-blue/30 transition-all duration-700"></div>
                        
                        <div className="relative z-10">
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full border border-white/10 mb-6">
                                <span className="w-1 h-1 bg-primary-blue rounded-full animate-pulse"></span>
                                <span className="text-[10px] font-bold uppercase tracking-widest text-white/80">Pipeline Health</span>
                            </div>
                            <h3 className="text-2xl font-bold mb-4">Placement Success: <span className="text-primary-blue">{statsData?.pipeline_conversion || 0}%</span></h3>
                            <p className="text-sm text-white/60 font-medium leading-relaxed mb-8">
                                Current pipeline efficiency across all stages. 
                                Monitoring {statsData?.interviewed_count || 0} active interview tracks for targeted roles.
                            </p>
                            
                            <div className="space-y-4 pt-4 border-t border-white/10">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-white/40 uppercase font-black tracking-widest">Target Hires</span>
                                    <span className="text-sm font-bold">5 Per Role</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-xs text-white/40 uppercase font-black tracking-widest">Status</span>
                                    <span className="text-xs font-bold px-2 py-0.5 bg-success text-white rounded-md uppercase">On Track</span>
                                </div>
                            </div>
                        </div>

                        <div className="relative z-10 mt-8">
                            <button 
                                onClick={handleShowTracker}
                                className="w-full py-4 bg-primary-blue hover:bg-white hover:text-primary-blue text-white rounded-2xl font-bold text-sm transition-all shadow-xl shadow-primary-blue/20 flex items-center justify-center gap-2 group/btn"
                            >
                                Placement Tracker
                                <ArrowUpRight size={18} className="group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Detailed Analytics Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Hiring Velocity */}
                <div className="bg-white rounded-3xl border border-border-subtle shadow-soft overflow-hidden">
                    <div className="p-8 border-b border-border-subtle flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-bold text-[#0A0F1E]">Hiring Velocity</h3>
                            <p className="text-xs text-text-muted font-medium mt-1">Average days taken at each stage of the funnel</p>
                        </div>
                        <BarChart3 size={20} className="text-primary-blue" />
                    </div>
                    <div className="p-8 space-y-8">
                        {(statsData?.velocity_stages || []).map((item, idx) => (
                            <div key={idx} className="space-y-2">
                                <div className="flex justify-between items-end">
                                    <span className="text-[11px] font-bold text-text-main uppercase tracking-wider">{item.stage}</span>
                                    <span className="text-xs font-black text-primary-dark">{item.days} Days</span>
                                </div>
                                <div className="h-2 w-full bg-bg-muted rounded-full overflow-hidden">
                                    <div 
                                        className={`h-full ${idx === 0 ? 'bg-primary-blue' : idx === 1 ? 'bg-purple-500' : 'bg-success'} rounded-full`} 
                                        style={{ width: `${Math.min(100, (item.days / 40) * 100)}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white p-8 rounded-3xl border border-border-subtle shadow-soft">
                    <h3 className="text-lg font-bold text-[#0A0F1E] mb-6">Success by Job Category</h3>
                    <div className="space-y-4">
                        {(statsData?.category_performance || []).map((tier, i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-bg-muted rounded-xl hover:bg-primary-blue/5 transition-colors group">
                                <span className="text-xs font-bold text-text-main group-hover:text-primary-blue">{tier.label}</span>
                                <span className="text-xs font-black text-success">{tier.success}% Match Rate</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Diversity and Source Section */}
            <section className="bg-white p-8 rounded-3xl border border-border-subtle shadow-soft">
                <h3 className="text-lg font-bold text-[#0A0F1E] mb-6">Candidate Sourcing Mix</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {(statsData?.sourcing_mix?.length > 0 ? statsData.sourcing_mix : [
                        {source: 'GitHub', count: 42},
                        {source: 'LinkedIn', count: 35},
                        {source: 'Referral', count: 23},
                        {source: 'Internal DB', count: 18},
                        {source: 'Job Boards', count: 12}
                    ]).map((item, i) => (
                        <div key={i} className="flex flex-col p-4 bg-bg-muted rounded-2xl border border-border-subtle">
                            <span className="text-2xl font-black text-primary-blue">
                                {statsData?.total_candidates > 0 ? Math.round((item.count / statsData.total_candidates) * 100) : item.count}%
                            </span>
                            <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider mt-1 truncate" title={item.source}>
                                {item.source}
                            </span>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default Stats;
