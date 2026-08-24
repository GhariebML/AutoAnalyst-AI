import React, { useState } from 'react';
import { Award, Zap } from 'lucide-react';

interface FeatureImportanceChartProps {
  importances: Record<string, number>;
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({ importances }) => {
  const [hoveredFeature, setHoveredFeature] = useState<string | null>(null);

  if (!importances || Object.keys(importances).length === 0) {
    return (
      <div className="glass-card p-6 text-center text-slate-400 text-sm italic rounded-2xl">
        Feature importance calculations not available.
      </div>
    );
  }

  // Sort descending and take top 10
  const sorted = Object.entries(importances)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  const maxVal = sorted[0]?.[1] || 1;

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
            <Award className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">Top Feature Drivers (Permutation Impact)</h4>
            <p className="text-xs text-slate-400">Relative contribution to champion model predictive accuracy</p>
          </div>
        </div>

        <div className="flex items-center gap-1 text-xs text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20">
          <Zap className="w-3.5 h-3.5" />
          <span>Top {sorted.length} Features</span>
        </div>
      </div>

      {/* Ranked Bars */}
      <div className="space-y-2.5">
        {sorted.map(([feature, score], idx) => {
          const pct = Math.max(Math.min((score / maxVal) * 100, 100), 4);
          const isHovered = hoveredFeature === feature;
          const isTop3 = idx < 3;

          return (
            <div
              key={feature}
              onMouseEnter={() => setHoveredFeature(feature)}
              onMouseLeave={() => setHoveredFeature(null)}
              className={`p-2 rounded-xl transition-all duration-200 cursor-pointer ${
                isHovered ? 'bg-slate-800/80 ring-1 ring-cyan-400/50' : 'hover:bg-slate-900/50'
              }`}
            >
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-5 h-5 rounded-md flex items-center justify-center font-mono text-[10px] font-bold ${
                      idx === 0
                        ? 'bg-amber-500 text-slate-950'
                        : idx === 1
                        ? 'bg-slate-300 text-slate-950'
                        : idx === 2
                        ? 'bg-amber-700 text-white'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {idx + 1}
                  </span>
                  <span className="font-mono text-slate-200 font-semibold">{feature}</span>
                </div>
                <span className="font-mono text-xs font-bold text-cyan-300">
                  {(score * 100).toFixed(2)}%
                </span>
              </div>

              {/* Progress Bar Container */}
              <div className="h-2 rounded-full bg-slate-800/90 overflow-hidden relative">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isTop3
                      ? 'bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 shadow-glow-cyan'
                      : 'bg-gradient-to-r from-slate-600 to-slate-400'
                  }`}
                  style={{ width: `${pct}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
