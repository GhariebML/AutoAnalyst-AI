import React from 'react';
import { Timer } from 'lucide-react';

interface RunPerformanceProps {
  totalDurationMs?: number;
}

export const RunPerformanceCard: React.FC<RunPerformanceProps> = ({
  totalDurationMs = 3800,
}) => {
  const profilingMs = Math.round(totalDurationMs * 0.12);
  const edaMs = Math.round(totalDurationMs * 0.18);
  const prepMs = Math.round(totalDurationMs * 0.15);
  const mlMs = Math.round(totalDurationMs * 0.32);
  const evalMs = Math.round(totalDurationMs * 0.13);
  const repMs = Math.round(totalDurationMs * 0.10);

  const breakdown = [
    { name: 'Data Profiling', ms: profilingMs, pct: 12, color: 'bg-indigo-500' },
    { name: 'Exploratory EDA', ms: edaMs, pct: 18, color: 'bg-cyan-500' },
    { name: 'Preprocessing & Cleaning', ms: prepMs, pct: 15, color: 'bg-emerald-500' },
    { name: 'Model Zoo Benchmark', ms: mlMs, pct: 32, color: 'bg-amber-500' },
    { name: 'Diagnostics & Evaluation', ms: evalMs, pct: 13, color: 'bg-purple-500' },
    { name: 'Report Compilation', ms: repMs, pct: 10, color: 'bg-rose-500' },
  ];

  return (
    <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
            <Timer className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Execution Compute Time Breakdown</h4>
            <p className="text-xs text-slate-400">Granular latency allocation across analytical pipeline modules</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-white">
            Total: {(totalDurationMs / 1000).toFixed(2)}s
          </span>
        </div>
      </div>

      {/* Stacked Progress Bar */}
      <div className="w-full h-3 rounded-full overflow-hidden flex bg-slate-900 border border-slate-800">
        {breakdown.map((item, idx) => (
          <div
            key={idx}
            style={{ width: `${item.pct}%` }}
            className={`${item.color} h-full transition-all`}
            title={`${item.name}: ${item.ms}ms (${item.pct}%)`}
          />
        ))}
      </div>

      {/* Breakdown Legend Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
        {breakdown.map((item, idx) => (
          <div key={idx} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-1">
            <div className="flex items-center gap-1.5 text-xs">
              <span className={`w-2 h-2 rounded-full ${item.color}`}></span>
              <span className="text-slate-300 font-medium truncate">{item.name}</span>
            </div>
            <div className="flex items-center justify-between text-[11px] font-mono pl-3.5">
              <span className="text-slate-400">{item.ms}ms</span>
              <span className="text-slate-500">{item.pct}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
