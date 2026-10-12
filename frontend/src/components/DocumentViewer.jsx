import React, { useState } from 'react';
import { Download, Sparkles, Copy, Check, FileText, ArrowRight, Eye, RefreshCw } from 'lucide-react';

export default function DocumentViewer({
  originalText,
  humanizedText,
  paragraphs,
  beforeStats,
  onHumanize,
  isHumanizing,
  onDownload,
  hasSession,
  filename
}) {
  const [activeTab, setActiveTab] = useState(humanizedText ? 'humanized' : 'original');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const textToCopy = activeTab === 'humanized' && humanizedText ? humanizedText : originalText;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getWordCount = (str) => {
    if (!str) return 0;
    return str.trim().split(/\s+/).filter(Boolean).length;
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-semibold text-white">Document Analysis & Editor</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            {filename ? `Loaded: ${filename}` : 'Interactive Text Session'} ·{' '}
            <span className="text-slate-300 font-medium">
              {getWordCount(activeTab === 'humanized' && humanizedText ? humanizedText : originalText)} words
            </span>
          </p>
        </div>

        {/* Action Button Group */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-xs font-medium text-slate-300 transition-colors flex items-center gap-1.5"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy Text'}</span>
          </button>

          {/* Humanize Action Button */}
          <button
            disabled={isHumanizing}
            onClick={onHumanize}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/25 active:scale-95"
          >
            {isHumanizing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Humanizing (Gemini API)...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5 fill-slate-950" />
                <span>Humanize Text (Target 6-8%)</span>
              </>
            )}
          </button>

          {/* Download Processed File Button */}
          {humanizedText && hasSession && (
            <button
              onClick={onDownload}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-indigo-600/30 active:scale-95"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Formatted File</span>
            </button>
          )}
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setActiveTab('original')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'original'
              ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <span className="w-2 h-2 rounded-full bg-rose-400" />
          Original Text
          {beforeStats && (
            <span className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 text-[10px]">
              {beforeStats.ai_percentage}% AI
            </span>
          )}
        </button>

        {humanizedText && (
          <button
            onClick={() => setActiveTab('humanized')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
              activeTab === 'humanized'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Humanized Text
            <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
              Bypassed
            </span>
          </button>
        )}
      </div>

      {/* Text Presentation Surface */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-6 min-h-[300px] max-h-[500px] overflow-y-auto leading-relaxed text-sm text-slate-200 font-sans space-y-4">
        {activeTab === 'humanized' && humanizedText ? (
          <div>
            <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between text-xs text-emerald-400">
              <span className="flex items-center gap-1.5">
                <Check className="w-4 h-4" />
                Humanized with high perplexity & natural rhythm. Buzzwords stripped.
              </span>
              <span className="text-[11px] text-slate-400">Word file ready for download</span>
            </div>
            <div className="whitespace-pre-line text-slate-100">
              {humanizedText}
            </div>
          </div>
        ) : (
          <div className="whitespace-pre-line text-slate-300">
            {originalText || 'No text extracted yet.'}
          </div>
        )}
      </div>
    </div>
  );
}
