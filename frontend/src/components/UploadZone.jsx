import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, FileCheck, AlertCircle, Type, Sparkles } from 'lucide-react';

export default function UploadZone({ onFileUpload, onTextAnalyze, isAnalyzing }) {
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState('file'); // 'file' or 'text'
  const [pastedText, setPastedText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (ext !== '.docx' && ext !== '.txt') {
      alert('Only .docx and .txt files are supported.');
      return;
    }
    setSelectedFile(file);
    onFileUpload(file);
  };

  const handlePastedTextSubmit = (e) => {
    e.preventDefault();
    if (!pastedText.trim()) return;
    onTextAnalyze(pastedText);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      {/* Decorative gradient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-20 bg-emerald-500/10 blur-3xl pointer-events-none" />

      {/* Tabs */}
      <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-emerald-400" />
            Upload Document or Paste Text
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Analyze AI probability, burstiness & perplexity across your document.
          </p>
        </div>

        <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-xs font-medium">
          <button
            onClick={() => setActiveTab('file')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'file'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            File Upload (.docx, .txt)
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'text'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Type className="w-3.5 h-3.5" />
            Paste Text
          </button>
        </div>
      </div>

      {activeTab === 'file' ? (
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".docx,.txt"
            className="hidden"
          />

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-300 ${
              isDragging
                ? 'border-emerald-400 bg-emerald-500/10 scale-[1.01]'
                : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/60'
            }`}
          >
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-emerald-400 shadow-inner group">
              <UploadCloud className="w-8 h-8 transition-transform group-hover:-translate-y-1" />
            </div>

            <h3 className="text-base font-semibold text-white mb-1">
              Drag & drop your document here, or <span className="text-emerald-400 underline underline-offset-4">browse</span>
            </h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
              Supports Microsoft Word (<strong className="text-slate-300">.docx</strong>) and Plain Text (<strong className="text-slate-300">.txt</strong>). Word styles and headings are preserved.
            </p>

            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-[11px] text-slate-400">
              <FileCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Full formatting preserved on humanized download</span>
            </div>
          </div>

          {selectedFile && (
            <div className="mt-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              <button
                disabled={isAnalyzing}
                onClick={() => processFile(selectedFile)}
                className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-lg shadow-emerald-500/20"
              >
                {isAnalyzing ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Re-Analyze File
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      ) : (
        <form onSubmit={handlePastedTextSubmit}>
          <textarea
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Paste your essay, article, or research text here to test AI detection and humanize..."
            rows={8}
            className="w-full bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 font-mono transition-all resize-y"
          />

          <div className="flex items-center justify-between mt-4">
            <div className="text-xs text-slate-500">
              {pastedText.trim() ? `${pastedText.trim().split(/\s+/).length} words` : '0 words'}
            </div>
            <button
              type="submit"
              disabled={isAnalyzing || !pastedText.trim()}
              className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-semibold text-xs transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20"
            >
              {isAnalyzing ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  Analyzing Text...
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  Analyze Text
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
