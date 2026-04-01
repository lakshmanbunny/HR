import React, { useState, useEffect } from 'react';
import { 
  Users, ExternalLink, Search, Filter, 
  Linkedin, Globe, ArrowLeft, Download,
  UserPlus, CheckCircle2, AlertCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const SourcedResults = () => {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Retrieve data from sessionStorage (saved by ChatWidget)
    const savedData = sessionStorage.getItem('last_sourced_candidates');
    if (savedData) {
      try {
        setCandidates(JSON.parse(savedData));
      } catch (e) {
        console.error("Error parsing sourced candidates", e);
      }
    }
    setLoading(false);
  }, []);

  const filteredCandidates = candidates.filter(c => 
    c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.snippet.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05070A] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-blue"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05070A] p-8 lg:p-12">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <button 
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors mb-8 group"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-xs font-black uppercase tracking-widest">Back to Intelligence</span>
        </button>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary-blue/10 rounded-full border border-primary-blue/20 mb-4">
              <Search size={12} className="text-primary-blue" />
              <span className="text-[10px] font-black uppercase tracking-widest text-primary-blue">X-Ray Sourcing Engine</span>
            </div>
            <h1 className="text-5xl font-black text-white tracking-tighter uppercase italic">
              Sourced <span className="text-primary-blue">Talent</span> Pool
            </h1>
            <p className="text-slate-500 mt-4 max-w-xl font-medium">
              Real-time candidate discovery using AI-generated Boolean/X-Ray queries across LinkedIn and Naukri.
            </p>
          </div>

          <div className="flex gap-4">
            <div className="bg-[#0A0F1E] border border-slate-800 rounded-2xl px-6 py-4 flex flex-col items-center">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Total Found</span>
              <span className="text-2xl font-black text-white">{candidates.length}</span>
            </div>
            <button className="bg-white text-black px-8 py-4 rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-primary-blue hover:text-white transition-all flex items-center gap-2 shadow-xl shadow-white/5">
              <Download size={18} />
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Search & Filter Bar */}
        <div className="bg-[#0A0F1E] border border-slate-800 rounded-3xl p-4 flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="text"
              placeholder="Filter by name, skills, or keywords..."
              className="w-full bg-slate-900/50 border border-slate-800 rounded-2xl py-4 pl-12 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-primary-blue transition-colors font-medium"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="px-6 py-4 bg-slate-900/50 border border-slate-800 rounded-2xl text-slate-400 hover:text-white hover:border-slate-700 transition-all flex items-center gap-2 font-bold text-sm">
            <Filter size={18} />
            Advanced Filters
          </button>
        </div>

        {/* Results Grid */}
        {filteredCandidates.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCandidates.map((candidate, idx) => (
              <div 
                key={idx}
                className="bg-[#0A0F1E] border border-slate-800 rounded-3xl p-6 hover:border-primary-blue/50 transition-all group relative overflow-hidden"
              >
                {/* Visual Flair */}
                <div className="absolute top-0 right-0 w-24 h-24 bg-primary-blue/5 rounded-full blur-2xl -mr-12 -mt-12 group-hover:bg-primary-blue/10 transition-colors"></div>
                
                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-6">
                    <div className="w-12 h-12 bg-slate-900 rounded-xl border border-slate-800 flex items-center justify-center text-primary-blue group-hover:bg-primary-blue group-hover:text-white transition-all">
                      {candidate.displayLink?.includes('linkedin') ? <Linkedin size={24} /> : <Globe size={24} />}
                    </div>
                    <div className="flex gap-2">
                       <button className="p-2 bg-slate-900 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800 transition-all border border-slate-800">
                         <UserPlus size={16} />
                       </button>
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2 line-clamp-2 min-h-[3.5rem]">
                    {candidate.title.split('|')[0].split('-')[0].trim()}
                  </h3>
                  
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{candidate.displayLink}</span>
                    <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                    <span className="text-[10px] font-bold text-success uppercase">Active</span>
                  </div>

                  <p className="text-slate-400 text-sm leading-relaxed mb-8 line-clamp-3">
                    {candidate.snippet}
                  </p>

                  <a 
                    href={candidate.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full py-4 bg-slate-900 hover:bg-primary-blue text-white rounded-2xl font-bold text-xs uppercase tracking-widest transition-all flex items-center justify-center gap-2 border border-slate-800 group-hover:border-primary-blue/30"
                  >
                    View Profile
                    <ExternalLink size={14} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-[#0A0F1E] border border-slate-800 rounded-3xl p-20 flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center text-slate-700 mb-6">
              <AlertCircle size={40} />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">No Candidates Found</h3>
            <p className="text-slate-500 max-w-sm font-medium">
              We couldn't find any candidates matching your Current parameters. Try broadening your location or experience requirements.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SourcedResults;
