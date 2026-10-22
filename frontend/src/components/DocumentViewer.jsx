import React, { useState } from 'react';
import { Download, Sparkles, Copy, Check, FileText, ArrowRight, Eye, RefreshCw, AlertTriangle, CheckCircle2, Lock } from 'lucide-react';

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
  const [highlightAI, setHighlightAI] = useState(true);

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

  const flaggedSentencesCount = beforeStats?.flagged_count ||
    (paragraphs ? paragraphs.filter(p => p.is_ai).length : 0);

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
            {beforeStats && (
              <span className="ml-2 text-cyan-400 font-medium">
                · {flaggedSentencesCount} AI sections flagged
              </span>
            )}
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

          {/* Humanize Action Button (Locked - Coming Soon) */}
          <div className="relative group">
            <button
              disabled
              className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-slate-400 font-semibold text-xs flex items-center gap-2 cursor-not-allowed shadow-inner opacity-90 transition-all select-none"
              title="Humanizer feature is locked: Coming soon in the next update!"
            >
              <div className="p-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Lock className="w-3.5 h-3.5" />
              </div>
              <span>Humanize Text</span>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-400/10 text-amber-400 border border-amber-400/30">
                Coming Soon
              </span>
            </button>
          </div>

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

      {/* View Switcher Tabs & Turnitin Highlight Switch */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('original')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${activeTab === 'original'
                ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
              }`}
          >
            <span className={`w-2 h-2 rounded-full ${beforeStats?.ai_percentage > 20 ? 'bg-rose-400' : 'bg-emerald-400'}`} />
            Original Document
            {beforeStats && (
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${beforeStats.ai_percentage > 20
                  ? 'bg-rose-500/20 text-rose-300'
                  : 'bg-emerald-500/20 text-emerald-300'
                }`}>
                {beforeStats.ai_percentage}% AI
              </span>
            )}
          </button>

          {humanizedText && (
            <button
              onClick={() => setActiveTab('humanized')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${activeTab === 'humanized'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Humanized Version
              <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">
                Bypassed
              </span>
            </button>
          )}
        </div>

        {/* Turnitin Style Highlight Toggle */}
        {activeTab === 'original' && (
          <div className="flex items-center gap-2 text-xs text-slate-300 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800">
            <span className="w-2.5 h-2.5 rounded bg-cyan-400/80 ring-2 ring-cyan-400/20" />
            <span>Turnitin / iThenticate AI Highlights:</span>
            <button
              onClick={() => setHighlightAI(!highlightAI)}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-all ${highlightAI
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'bg-slate-800 text-slate-400'
                }`}
            >
              {highlightAI ? 'ON' : 'OFF'}
            </button>
          </div>
        )}
      </div>

      {/* Text Presentation Surface */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-950/70 p-6 min-h-[350px] max-h-[550px] overflow-y-auto leading-relaxed text-sm font-sans space-y-4">
        {activeTab === 'humanized' && humanizedText ? (
          <div>
            <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between text-xs text-emerald-400">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Humanized with high perplexity & varied sentence lengths. Academic markers neutralized.
              </span>
              <span className="text-[11px] text-slate-400 font-mono">Ready for Turnitin resubmission</span>
            </div>
            <div className="whitespace-pre-line text-slate-100 font-normal leading-7">
              {humanizedText}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* If we have structured paragraphs with sentence highlights, render highlighted view */}
            {paragraphs && paragraphs.length > 0 ? (
              paragraphs.map((p, pIdx) => {
                const isHeading = p.is_heading;
                const isBullet = p.is_bullet;
                const isTable = p.is_table_cell;

                return (
                  <div
                    key={p.id || pIdx}
                    className={`${isHeading ? 'font-bold text-white text-base mt-4' : 'text-slate-200'} ${isTable ? 'pl-3 border-l-2 border-slate-700 text-slate-300 text-xs py-1' : ''
                      } leading-7`}
                  >
                    {p.sentences && p.sentences.length > 0 ? (
                      p.sentences.map((s, sIdx) => {
                        const isAI = s.is_ai && highlightAI;
                        return (
                          <span
                            key={sIdx}
                            className={`transition-colors ${isAI
                                ? 'bg-cyan-500/20 text-cyan-200 border-b-2 border-cyan-400/80 rounded-sm px-1 py-0.5 mx-0.5 inline shadow-sm'
                                : ''
                              }`}
                            title={isAI ? `Flagged as AI (${s.ai_score}% confidence)` : 'Human'}
                          >
                            {s.text}{' '}
                          </span>
                        );
                      })
                    ) : (
                      <span className={p.is_ai && highlightAI ? 'bg-cyan-500/20 text-cyan-200 border-b-2 border-cyan-400/80 px-1 py-0.5 rounded-sm' : ''}>
                        {p.text}
                      </span>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="whitespace-pre-line text-slate-300">
                {originalText || 'No text extracted yet.'}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
