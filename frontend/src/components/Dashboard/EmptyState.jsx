import React from 'react';
import { Upload, Link as LinkIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

const EmptyState = () => {
    return (
        <section className="mt-4 md:mt-8 p-6 md:p-12 bg-bg-muted rounded-2xl border-2 border-dashed border-gray-200 flex flex-col items-center gap-6 text-center max-w-4xl mx-auto w-full mb-16">
            <div className="w-16 md:w-24 h-16 md:h-24 bg-white rounded-xl flex items-center justify-center shadow-soft relative overflow-hidden group">
                <div className="w-10 md:w-12 h-10 md:h-12 bg-primary-blue/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                    <div className="w-5 md:w-6 h-5 md:h-6 bg-primary-blue rounded rotate-45"></div>
                </div>
            </div>

            <div className="max-w-md">
                <h3 className="text-lg md:text-xl font-bold text-[#1A1A1A] mb-2">No candidates screened yet</h3>
                <p className="text-xs md:text-sm text-gray-500 leading-relaxed">
                    Start by uploading resume files or importing profiles via URL. Paradigm IT will extract intelligence and verify credentials automatically.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-2xl px-4">
                <Link 
                    to="/upload/fresher"
                    className="flex flex-col items-center justify-center gap-4 p-10 bg-primary-blue text-white rounded-[2rem] font-bold transition-all shadow-xl shadow-primary-blue/20 hover:shadow-2xl hover:shadow-primary-blue/30 hover:-translate-y-2 active:scale-95 group"
                >
                    <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Upload size={32} />
                    </div>
                    <div className="flex flex-col items-center">
                        <span className="text-xl">Upload</span>
                        <span className="text-xs uppercase tracking-[0.2em] opacity-80">For Freshers</span>
                    </div>
                </Link>

                <Link 
                    to="/upload/experienced"
                    className="flex flex-col items-center justify-center gap-4 p-10 bg-white border-4 border-primary-blue text-primary-blue rounded-[2rem] font-bold transition-all shadow-xl shadow-black/5 hover:shadow-2xl hover:shadow-black/10 hover:-translate-y-2 active:scale-95 group"
                >
                    <div className="w-16 h-16 bg-primary-blue/5 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Upload size={32} />
                    </div>
                    <div className="flex flex-col items-center">
                        <span className="text-xl">Upload</span>
                        <span className="text-xs uppercase tracking-[0.2em] opacity-80">For Experienced</span>
                    </div>
                </Link>
            </div>
        </section>
    );
};

export default EmptyState;
