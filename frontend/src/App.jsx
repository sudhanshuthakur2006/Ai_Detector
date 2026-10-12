import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UploadZone from './components/UploadZone';
import StatsDashboard from './components/StatsDashboard';
import DocumentViewer from './components/DocumentViewer';
import ApiKeyModal from './components/ApiKeyModal';
import { api } from './services/api';
import { Shield, Sparkles, CheckCircle2, AlertTriangle, ArrowRight, FileCheck } from 'lucide-react';

export default function App() {
  const [backendOnline, setBackendOnline] = useState(false);
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('stealthdoc_gemini_key') || '');
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);

  // Document state
  const [sessionData, setSessionData] = useState(null);
  const [originalText, setOriginalText] = useState('');
  const [humanizedText, setHumanizedText] = useState('');
  const [beforeStats, setBeforeStats] = useState(null);
  const [afterStats, setAfterStats] = useState(null);

  // Interaction loaders & alerts
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isHumanizing, setIsHumanizing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Check backend health on mount
  useEffect(() => {
    const pingBackend = async () => {
      try {
        const health = await api.checkHealth();
        setBackendOnline(health.status === 'online');
        if (health.has_gemini_key && !apiKey) {
          // If server already has env var set, consider key available
          setApiKey('ENV_CONFIGURED');
        }
      } catch (err) {
        setBackendOnline(false);
      }
    };

    pingBackend();
    const interval = setInterval(pingBackend, 15000);
    return () => clearInterval(interval);
  }, [apiKey]);

  const handleSaveApiKey = (newKey) => {
    setApiKey(newKey);
    localStorage.setItem('stealthdoc_gemini_key', newKey);
  };

  // Upload file (.docx, .txt)
  const handleFileUpload = async (file) => {
    setErrorMsg('');
    setIsAnalyzing(true);
    setHumanizedText('');
    setAfterStats(null);

    try {
      const data = await api.uploadFile(file);
      setSessionData(data);
      setOriginalText(data.full_text);
      setBeforeStats(data.baseline_stats);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to upload and analyze document.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Direct text analyze
  const handleTextAnalyze = async (text) => {
    setErrorMsg('');
    setIsAnalyzing(true);
    setSessionData(null);
    setOriginalText(text);
    setHumanizedText('');
    setAfterStats(null);

    try {
      const stats = await api.detectText(text);
      setBeforeStats(stats);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to analyze text.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Humanize action
  const handleHumanize = async () => {
    if (!apiKey) {
      setIsKeyModalOpen(true);
      return;
    }

    setErrorMsg('');
    setIsHumanizing(true);

    try {
      const keyToSend = apiKey === 'ENV_CONFIGURED' ? '' : apiKey;
      const res = await api.humanizeDocument({
        sessionId: sessionData?.session_id,
        text: originalText,
        apiKey: keyToSend,
      });

      setHumanizedText(res.humanized_full_text);
      setAfterStats(res.after_stats);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Humanization failed.';
      setErrorMsg(msg);
      if (msg.toLowerCase().includes('api key')) {
        setIsKeyModalOpen(true);
      }
    } finally {
      setIsHumanizing(false);
    }
  };

  // Download reconstructed file
  const handleDownload = () => {
    if (!sessionData?.session_id) {
      // If direct text session, download as .txt
      const blob = new Blob([humanizedText], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'stealthdoc_humanized.txt';
      link.click();
      URL.revokeObjectURL(url);
      return;
    }

    const downloadUrl = api.getDownloadUrl(sessionData.session_id);
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar
        backendOnline={backendOnline}
        hasApiKey={Boolean(apiKey)}
        onOpenApiKeyModal={() => setIsKeyModalOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Targeting 6-8% AI Detection Bypass</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            AI Text Detector & Document <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Humanizer</span>
          </h1>
          <p className="text-sm text-slate-400">
            Upload Word (<strong className="text-slate-300">.docx</strong>) or Text (<strong className="text-slate-300">.txt</strong>) documents to scan for AI content. Humanize with Gemini API to eliminate AI buzzwords and maximize natural burstiness while preserving original formatting.
          </p>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-xs text-rose-300 animate-in fade-in">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
            <button
              onClick={() => setErrorMsg('')}
              className="px-2 py-1 hover:bg-rose-500/20 rounded font-semibold text-rose-200"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Upload Zone */}
        <UploadZone
          onFileUpload={handleFileUpload}
          onTextAnalyze={handleTextAnalyze}
          isAnalyzing={isAnalyzing}
        />

        {/* Stats Dashboard */}
        {(beforeStats || afterStats) && (
          <StatsDashboard
            beforeStats={beforeStats}
            afterStats={afterStats}
          />
        )}

        {/* Document Editor & Viewer */}
        {originalText && (
          <DocumentViewer
            originalText={originalText}
            humanizedText={humanizedText}
            paragraphs={sessionData?.paragraphs}
            beforeStats={beforeStats}
            onHumanize={handleHumanize}
            isHumanizing={isHumanizing}
            onDownload={handleDownload}
            hasSession={Boolean(sessionData?.session_id)}
            filename={sessionData?.filename}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-600">
        <p>StealthDoc Local Engine · RoBERTa AI Detector & Gemini Humanizer · Privacy-First Architecture</p>
      </footer>

      {/* API Key Modal */}
      <ApiKeyModal
        isOpen={isKeyModalOpen}
        onClose={() => setIsKeyModalOpen(false)}
        apiKey={apiKey === 'ENV_CONFIGURED' ? '' : apiKey}
        onSaveApiKey={handleSaveApiKey}
      />
    </div>
  );
}
