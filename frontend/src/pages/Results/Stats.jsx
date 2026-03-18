import React from 'react';
import { TrendingUp, Clock, Users, CheckCircle, BarChart3, ArrowUpRight, Calendar } from 'lucide-react';

const Stats = () => {
    // Mock data for display
    const metrics = [
        {
            title: "Average Time to Fill",
            value: "18 Days",
            change: "-2.4%",
            trend: "down",
            icon: Clock,
            color: "text-primary-blue",
            bg: "bg-primary-blue/10"
        },
        {
            title: "Application Volume",
            value: "1,284",
            change: "+12.5%",
            trend: "up",
            icon: Users,
            color: "text-purple-600",
            bg: "bg-purple-50"
        },
        {
            title: "Onboarding Rate",
            value: "94.2%",
            change: "+0.8%",
            trend: "up",
            icon: CheckCircle,
            color: "text-success",
            bg: "bg-success/10"
        },
        {
            title: "Sourcing Efficiency",
            value: "82%",
            change: "+5.1%",
            trend: "up",
            icon: TrendingUp,
            color: "text-orange-500",
            bg: "bg-orange-50"
        }
    ];

    return (
        <div className="flex flex-col gap-10 pb-20">
            {/* Header Section */}
            <section>
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-black text-[#0A0F1E] tracking-tight mb-3">Recruitment Intelligence <span className="text-primary-blue">Statistics</span></h1>
                        <p className="text-sm text-text-muted max-w-2xl font-medium leading-relaxed">
                            Deep-dive metrics and performance analytics for your hiring funnel. Track efficiency from position opening to onboarding.
                        </p>
                    </div>
                    <div className="flex items-center gap-3 px-4 py-2 bg-white border border-border-subtle rounded-xl shadow-sm">
                        <Calendar size={16} className="text-text-muted" />
                        <span className="text-xs font-bold text-text-main uppercase tracking-wider">Last 30 Days</span>
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
                        </div>
                    ))}
                </div>
            </section>

            {/* Detailed Analytics Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Time to Fill Breakdown */}
                <div className="lg:col-span-2 bg-white rounded-3xl border border-border-subtle shadow-soft overflow-hidden">
                    <div className="p-8 border-b border-border-subtle flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-bold text-[#0A0F1E]">Hiring Velocity</h3>
                            <p className="text-xs text-text-muted font-medium mt-1">Average days taken at each stage of the funnel</p>
                        </div>
                        <BarChart3 size={20} className="text-primary-blue" />
                    </div>
                    <div className="p-8 space-y-8">
                        {[
                            { stage: "Profile Screening", days: 2, color: "bg-primary-blue", width: "15%" },
                            { stage: "Technical Audit (GitHub)", days: 4, color: "bg-purple-500", width: "25%" },
                            { stage: "AI Real-time Interview", days: 5, color: "bg-indigo-500", width: "35%" },
                            { stage: "Internal Review & Approval", days: 3, color: "bg-orange-500", width: "20%" },
                            { stage: "Onboarding Processing", days: 4, color: "bg-success", width: "25%" }
                        ].map((item, idx) => (
                            <div key={idx} className="space-y-2">
                                <div className="flex justify-between items-end">
                                    <span className="text-[11px] font-bold text-text-main uppercase tracking-wider">{item.stage}</span>
                                    <span className="text-xs font-black text-primary-dark">{item.days} Days</span>
                                </div>
                                <div className="h-2 w-full bg-bg-muted rounded-full overflow-hidden">
                                    <div className={`h-full ${item.color} rounded-full`} style={{ width: item.width }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Performance Summary Card */}
                <div className="bg-[#0A0F1E] rounded-3xl p-8 text-white flex flex-col justify-between relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary-blue/20 rounded-full blur-[80px] -mr-32 -mt-32 group-hover:bg-primary-blue/30 transition-all duration-700"></div>
                    
                    <div className="relative z-10">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full border border-white/10 mb-6">
                            <span className="w-1 h-1 bg-primary-blue rounded-full animate-pulse"></span>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-white/80">System Optimization</span>
                        </div>
                        <h3 className="text-2xl font-bold mb-4">Pipeline Efficiency reached <span className="text-primary-blue">88.5%</span></h3>
                        <p className="text-sm text-white/60 font-medium leading-relaxed mb-8">
                            Your automated screening funnel is currently saving approximately 142 man-hours per week compared to traditional vetting.
                        </p>
                    </div>

                    <div className="relative z-10">
                        <button className="w-full py-4 bg-primary-blue hover:bg-white hover:text-primary-blue text-white rounded-2xl font-bold text-sm transition-all shadow-xl shadow-primary-blue/20 flex items-center justify-center gap-2 group/btn">
                            Download Detailed Report
                            <ArrowUpRight size={18} className="group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Diversity and Source Section */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-white p-8 rounded-3xl border border-border-subtle shadow-soft">
                    <h3 className="text-lg font-bold text-[#0A0F1E] mb-6">Candidate Sourcing Mix</h3>
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex flex-col items-center">
                            <div className="text-2xl font-black text-primary-blue">42%</div>
                            <div className="text-[10px] font-bold text-text-muted uppercase tracking-wider">GitHub Direct</div>
                        </div>
                        <div className="h-8 w-px bg-border-subtle"></div>
                        <div className="flex flex-col items-center">
                            <div className="text-2xl font-black text-purple-600">35%</div>
                            <div className="text-[10px] font-bold text-text-muted uppercase tracking-wider">LinkedIn</div>
                        </div>
                        <div className="h-8 w-px bg-border-subtle"></div>
                        <div className="flex flex-col items-center">
                            <div className="text-2xl font-black text-orange-500">23%</div>
                            <div className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Referral</div>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-3xl border border-border-subtle shadow-soft">
                    <h3 className="text-lg font-bold text-[#0A0F1E] mb-6">Hiring Success by Tier</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-bg-muted rounded-xl">
                            <span className="text-xs font-bold text-text-main">Enterprise Suite</span>
                            <span className="text-xs font-black text-success">92% Match Rate</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-bg-muted rounded-xl">
                            <span className="text-xs font-bold text-text-main">Tech Core</span>
                            <span className="text-xs font-black text-success">88% Match Rate</span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Stats;
