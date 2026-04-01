import React from 'react';
import { ChevronRight, Users, Info } from 'lucide-react';

const RecruitmentFunnel = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="bg-[#0f172a] border border-slate-800 rounded-3xl p-8 h-[500px] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-widest animate-pulse font-mono">Loading Funnel...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-[#0f172a] border border-slate-800 rounded-3xl p-8 h-[500px] flex items-center justify-center text-slate-400 font-bold text-sm italic">
        No funnel data available for the selected filters.
      </div>
    );
  }

  // Calculate conversion rates
  const stagesWithRates = data.map((item, index) => {
    const prevCount = index > 0 ? data[index - 1].count : null;
    const conversion = prevCount ? ((item.count / prevCount) * 100).toFixed(1) : null;
    const overallConversion = index > 0 ? ((item.count / data[0].count) * 100).toFixed(1) : (100).toFixed(1);
    return { ...item, conversion, overallConversion };
  });

  const maxCount = Math.max(...data.map(d => d.count), 1);

  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
      {/* Decorative background element */}
      <div className="absolute -top-24 -left-24 w-64 h-64 bg-blue-500/10 rounded-full blur-[100px]"></div>
      
      <div className="flex justify-between items-center mb-10 relative z-10">
        <div className="flex flex-col">
            <h3 className="text-2xl font-black text-white flex items-center gap-3 tracking-tight">
                <div className="w-1.5 h-8 bg-blue-500 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.5)]"></div>
                Recruitment Funnel
            </h3>
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] mt-2 ml-4">Progression Pipeline Analytics</p>
        </div>
        <div className="flex items-center gap-3">
            <div className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full">
                <span className="text-[9px] text-blue-400 font-black uppercase tracking-widest">Live Flow</span>
            </div>
        </div>
      </div>

      <div className="flex flex-col gap-4 relative z-10">
        {stagesWithRates.map((stage, index) => {
          // Calculate width based on count relative to max
          const widthPercent = (stage.count / maxCount) * 100;
          // Minimum width for visibility
          const displayWidth = Math.max(widthPercent, 5);
          
          // Color gradient based on depth
          const opacity = 1 - (index * 0.08);
          const blueShade = `rgba(59, 130, 246, ${opacity})`;

          return (
            <div key={stage.stage} className="relative group">
              <div className="flex items-center gap-6">
                {/* Stage Label & Primary Count */}
                <div className="w-44 flex flex-col items-end">
                  <span className="text-[11px] font-black text-slate-400 group-hover:text-blue-400 transition-colors uppercase tracking-wider text-right line-clamp-1">
                    {stage.stage}
                  </span>
                  <span className="text-lg font-black text-white mt-0.5 tracking-tight group-hover:scale-110 transition-transform origin-right">
                    {stage.count.toLocaleString()}
                  </span>
                </div>

                {/* Funnel Bar Container */}
                <div className="flex-1 h-14 relative flex items-center">
                  {/* The actual funnel segment */}
                  <div 
                    className="h-10 rounded-xl transition-all duration-1000 ease-out relative flex items-center group-hover:h-12"
                    style={{ 
                      width: `${displayWidth}%`, 
                      background: `linear-gradient(90deg, #1e293b 0%, ${blueShade} 100%)`,
                      boxShadow: stage.count > 0 ? '0 8px 24px rgba(0,0,0,0.4)' : 'none',
                      borderRight: '2px solid rgba(255,255,255,0.1)'
                    }}
                  >
                    {/* Shadow/Glow effect */}
                    <div className="absolute inset-0 bg-blue-400/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl"></div>
                    
                    {/* Count has been moved to the left for clarity per user request */}
                  </div>
                  
                  {/* Metric Metadata */}
                  <div className="ml-5 flex flex-col">
                    <span className="text-xs font-black text-white tracking-tight">
                        {stage.overallConversion}%
                    </span>
                    <span className="text-[9px] text-slate-500 font-bold uppercase tracking-widest -mt-0.5">
                        of total
                    </span>
                  </div>
                </div>
              </div>

              {/* Connector line to next stage */}
              {index < stagesWithRates.length - 1 && (
                <div className="absolute left-[184px] top-12 w-[1px] h-6 bg-slate-800/50 z-0"></div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-12 pt-8 border-t border-slate-800/50 flex justify-between items-center text-[10px] text-slate-500 font-black uppercase tracking-[0.2em]">
        <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-blue-500 rounded-sm shadow-[0_0_8px_rgba(59,130,246,0.3)]"></div>
                <span>Qualified Pool</span>
            </div>
            <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-slate-700 rounded-sm"></div>
                <span>Historical Context</span>
            </div>
        </div>
        <div className="flex items-center gap-1.5 text-blue-400/60">
            <Info size={12} />
            <span>Interactive Data Visual</span>
        </div>
      </div>
    </div>
  );
};

export default RecruitmentFunnel;
