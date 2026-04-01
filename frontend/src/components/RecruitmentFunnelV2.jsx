import React from 'react';
import { 
  Users, Search, FileText, UserCheck, 
  MessageSquare, UserPlus, Award, CheckCircle2 
} from 'lucide-react';

const STAGE_ICONS = {
  "Submissions": Users,
  "Pre-screening": Search,
  "Written": FileText,
  "L1 Interview": UserCheck,
  "L2 Interview": MessageSquare,
  "L3 Interview": UserPlus,
  "Offered": Award,
  "Joined": CheckCircle2,
  "default": Users
};

const RecruitmentFunnelV2 = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="bg-[#0A0F1E] border border-slate-800 rounded-3xl p-8 h-[700px] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-widest animate-pulse font-mono">Synthesizing Visuals...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-[#0A0F1E] border border-slate-800 rounded-3xl p-8 h-[700px] flex items-center justify-center text-slate-500 font-bold text-sm italic">
        No recruitment data synchronized.
      </div>
    );
  }

  // Calculate percentages and rates
  const stagesWithRates = data.map((item, index) => {
    const overallConversion = index > 0 ? ((item.count / data[0].count) * 100).toFixed(1) : (100).toFixed(1);
    return { ...item, overallConversion };
  });

  // Color palette for the classic funnel
  const colors = [
    '#2E7D32', // Deep Green
    '#00897B', // Teal
    '#00ACC1', // Cyan
    '#039BE5', // Light Blue
    '#1E88E5', // Blue
    '#3949AB', // Indigo
    '#5E35B1', // Deep Purple
    '#1B5E20', // Darker Green (Joined)
  ];

  return (
    <div className="bg-[#0A0F1E] border border-slate-800 rounded-3xl p-12 shadow-2xl relative overflow-hidden flex flex-col items-center">
      {/* Dynamic Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[120px]"></div>

      <div className="mb-12 text-center relative z-10">
        <h3 className="text-3xl font-black text-white tracking-tighter uppercase italic">
          Elite Pipeline <span className="text-blue-500">Analytics</span>
        </h3>
        <div className="h-1 w-24 bg-gradient-to-r from-blue-600 to-transparent mx-auto mt-2 rounded-full"></div>
      </div>

      <div className="w-full max-w-[800px] relative z-10">
        <svg viewBox="0 0 800 1000" className="w-full overflow-visible drop-shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
          <defs>
            <filter id="shadow">
              <feDropShadow dx="0" dy="4" stdDeviation="4" floodOpacity="0.4"/>
            </filter>
            {colors.map((color, i) => (
                <linearGradient key={i} id={`grad-${i}`} x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor={color} stopOpacity="1" />
                    <stop offset="100%" stopColor={color} stopOpacity="0.8" />
                </linearGradient>
            ))}
          </defs>

          {stagesWithRates.map((stage, i) => {
            const totalStages = stagesWithRates.length;
            const segmentHeight = 1000 / totalStages;
            const yStart = segmentHeight * i;
            const yEnd = segmentHeight * (i + 1);
            
            // X-Tapering Logic (Top width 800 -> Bottom width 300)
            const xOffsetStart = (i / totalStages) * 250;
            const xOffsetEnd = ((i + 1) / totalStages) * 250;
            
            const p1 = `${xOffsetStart},${yStart}`;
            const p2 = `${800 - xOffsetStart},${yStart}`;
            const p3 = `${800 - xOffsetEnd},${yEnd}`;
            const p4 = `${xOffsetEnd},${yEnd}`;

            const centerX = 400;
            const centerY = yStart + (segmentHeight / 2);
            
            const Icon = STAGE_ICONS[stage.stage] || STAGE_ICONS.default;

            return (
              <g key={stage.stage} className="transition-all duration-300 transform-gpu hover:translate-x-2">
                <path 
                  d={`M ${p1} L ${p2} L ${p3} L ${p4} Z`}
                  fill={`url(#grad-${i})`}
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="1"
                  className="hover:brightness-125 transition-all cursor-pointer"
                />
                
                {/* Content Overlay */}
                <g className="pointer-events-none">
                  {/* Icon */}
                  <foreignObject 
                    x={centerX - 100} 
                    y={centerY - 20} 
                    width="40" 
                    height="40"
                  >
                    <div className="flex items-center justify-end w-full h-full text-white/40">
                      <Icon size={24} />
                    </div>
                  </foreignObject>

                  {/* Stage Label */}
                  <text 
                    x={centerX - 50} 
                    y={centerY - 8} 
                    className="fill-white/80 font-black text-xs uppercase tracking-widest"
                  >
                    {stage.stage}
                  </text>
                  
                  {/* Count & Percentage */}
                  <text 
                    x={centerX - 50} 
                    y={centerY + 22} 
                    className="fill-white font-black text-2xl tracking-tighter"
                  >
                    {stage.count.toLocaleString()} 
                    <tspan className="text-[10px] fill-white/40 font-bold tracking-normal ml-3" dx="12">
                      ({stage.overallConversion}%)
                    </tspan>
                  </text>
                </g>
                
                {/* Visual Connector / Shine */}
                <path 
                    d={`M ${p1} L ${p2}`} 
                    stroke="rgba(255,255,255,0.15)" 
                    strokeWidth="1" 
                />
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-16 flex items-center justify-between w-full max-w-md pt-8 border-t border-slate-800">
         <div className="flex flex-col items-center">
            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Top Volume</span>
            <span className="text-lg font-black text-white">{data[0].count}</span>
         </div>
         <div className="flex flex-col items-center">
            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Bottom Goal</span>
            <span className="text-lg font-black text-white">{data[data.length-1].count}</span>
         </div>
         <div className="flex flex-col items-center">
            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Efficiency Ratio</span>
            <span className="text-lg font-black text-green-500">
              {data[data.length-1].count > 0 
                ? `1 : ${Math.round(data[0].count / data[data.length-1].count)}` 
                : 'N/A'}
            </span>
         </div>
      </div>
    </div>
  );
};

export default RecruitmentFunnelV2;
