import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { ShieldAlert, ShieldCheck, Sparkles, TrendingDown, Activity, Layers, AlertCircle } from 'lucide-react';

const COLORS = {
  human: '#10b981', // Emerald
  ai: '#f43f5e',    // Rose
  mixed: '#f59e0b', // Amber
};

function PieCard({ title, stats, subtitle, isTargetMet }) {
  if (!stats) return null;

  const data = [
    { name: 'Human', value: stats.human_percentage || 0, color: COLORS.human },
    { name: 'AI Generated', value: stats.ai_percentage || 0, color: COLORS.ai },
    { name: 'Mixed', value: stats.mixed_percentage || 0, color: COLORS.mixed },
  ];

  const aiScore = stats.ai_percentage || 0;
  const isBypassed = aiScore <= 10;
  const isHighAI = aiScore > 30;

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 relative overflow-hidden flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            {subtitle}
          </span>
          <span
            className={`px-2.5 py-0.5 rounded-full text-xs font-semibold flex items-center gap-1.5 ${
              isBypassed
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                : isHighAI
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
            }`}
          >
            {isBypassed ? <ShieldCheck className="w-3.5 h-3.5" /> : <ShieldAlert className="w-3.5 h-3.5" />}
            {isBypassed ? 'Stealth / Bypass Target' : isHighAI ? 'Turnitin AI Detected' : 'Mixed Content'}
          </span>
        </div>

        <h3 className="text-xl font-bold text-white mb-2">{title}</h3>

        {/* Dual Pie Chart */}
        <div className="h-56 w-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={4}
                dataKey="value"
                stroke="none"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(val) => [`${val}%`, '']}
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '12px',
                  color: '#f8fafc',
                  fontSize: '12px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Center Callout matching detector state */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            {isHighAI ? (
              <>
                <span className="text-3xl font-extrabold text-rose-400 tracking-tight">
                  {stats.ai_percentage}%
                </span>
                <span className="text-[11px] font-semibold text-rose-300">AI Detected</span>
              </>
            ) : (
              <>
                <span className="text-3xl font-extrabold text-emerald-400 tracking-tight">
                  {stats.human_percentage}%
                </span>
                <span className="text-[11px] font-semibold text-emerald-400">Human Score</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Breakdown Pills */}
      <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-slate-800/80 text-center">
        <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-[11px] text-emerald-400 font-medium">Human</p>
          <p className="text-base font-bold text-white">{stats.human_percentage}%</p>
        </div>
        <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-[11px] text-rose-400 font-medium">AI Content</p>
          <p className="text-base font-bold text-rose-400">{stats.ai_percentage}%</p>
        </div>
        <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
          <p className="text-[11px] text-amber-400 font-medium">Mixed</p>
          <p className="text-base font-bold text-white">{stats.mixed_percentage}%</p>
        </div>
      </div>

      {/* Metrics footer: Flagged count & Turnitin calibration badge */}
      <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 px-1 pt-2 border-t border-slate-900">
        <span className="flex items-center gap-1">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span>Flagged Sections: <strong className="text-cyan-300">{stats.flagged_count ?? 0}</strong></span>
        </span>
        <span className="text-[10px] text-slate-400 font-medium bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
          iThenticate / Turnitin Calibrated
        </span>
      </div>
    </div>
  );
}

export default function StatsDashboard({ beforeStats, afterStats }) {
  if (!beforeStats && !afterStats) return null;

  const aiReduction =
    beforeStats && afterStats
      ? (beforeStats.ai_percentage - afterStats.ai_percentage).toFixed(1)
      : null;

  return (
    <div className="space-y-6">
      {/* Target Notification Banner if humanized */}
      {afterStats && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-transparent border border-emerald-500/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white">
                Humanization Applied Successfully
              </h4>
              <p className="text-xs text-slate-400">
                AI probability shifted from <span className="text-rose-400 font-bold">{beforeStats?.ai_percentage}%</span> down to{' '}
                <span className="text-emerald-400 font-bold">{afterStats.ai_percentage}%</span> (Target: 6-8%).
              </p>
            </div>
          </div>
          {aiReduction > 0 && (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
              <TrendingDown className="w-4 h-4" />
              <span>-{aiReduction}% AI Content</span>
            </div>
          )}
        </div>
      )}

      {/* Warning banner if baseline AI is high */}
      {beforeStats && beforeStats.ai_percentage > 25 && !afterStats && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 flex items-center gap-3 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>
            <strong>Attention:</strong> iThenticate/Turnitin pattern match detected {beforeStats.flagged_count} AI sections ({beforeStats.ai_percentage}% AI). Automated Humanizer rewrite engine is coming soon in the next update.
          </span>
        </div>
      )}

      {/* Dual Charts Grid */}
      <div className={`grid gap-6 ${afterStats ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'}`}>
        <PieCard
          title="Baseline Document Score"
          subtitle="Before Humanization"
          stats={beforeStats}
        />

        {afterStats && (
          <PieCard
            title="Humanized Document Score"
            subtitle="After Gemini Humanizer"
            stats={afterStats}
            isTargetMet={afterStats.ai_percentage <= 8}
          />
        )}
      </div>
    </div>
  );
}
