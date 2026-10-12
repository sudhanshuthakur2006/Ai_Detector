import React from 'react';
import { ShieldCheck, Key, Cpu, Sparkles } from 'lucide-react';

export default function Navbar({ backendOnline, hasApiKey, onOpenApiKeyModal }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <ShieldCheck className="w-6 h-6 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-white">Stealth<span className="text-emerald-400">Doc</span></span>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                v1.0 Local
              </span>
            </div>
            <p className="text-xs text-slate-400">AI Text Detector & Humanizer Engine</p>
          </div>
        </div>

        {/* Right Status Badges & Controls */}
        <div className="flex items-center gap-3">
          {/* Backend Health Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium glass-card border border-slate-800">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Backend:</span>
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
              <span className={backendOnline ? 'text-emerald-400' : 'text-rose-400'}>
                {backendOnline ? 'Connected' : 'Offline'}
              </span>
            </span>
          </div>

          {/* Gemini Key Config */}
          <button
            onClick={onOpenApiKeyModal}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all border ${
              hasApiKey
                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/20'
                : 'bg-amber-500/10 text-amber-300 border-amber-500/30 hover:bg-amber-500/20'
            }`}
          >
            <Key className="w-3.5 h-3.5" />
            <span>{hasApiKey ? 'Gemini Key Configured' : 'Configure Gemini API Key'}</span>
            <Sparkles className="w-3 h-3 opacity-60" />
          </button>
        </div>
      </div>
    </header>
  );
}
