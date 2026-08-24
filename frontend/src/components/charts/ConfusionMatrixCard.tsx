import React from 'react';
import { Target, CheckCircle, XCircle } from 'lucide-react';

interface ConfusionMatrixCardProps {
  matrix: number[][];
}

export const ConfusionMatrixCard: React.FC<ConfusionMatrixCardProps> = ({ matrix }) => {
  if (!matrix || matrix.length < 2 || matrix[0].length < 2) {
    return (
      <div className="glass-card p-6 text-center text-slate-400 text-sm italic rounded-2xl">
        Confusion matrix diagnostic not applicable or unavailable for this model.
      </div>
    );
  }

  const tn = matrix[0][0] || 0;
  const fp = matrix[0][1] || 0;
  const fn = matrix[1][0] || 0;
  const tp = matrix[1][1] || 0;
  const total = tn + fp + fn + tp || 1;

  const accuracy = (tp + tn) / total;
  const precision = tp / (tp + fp || 1);
  const recall = tp / (tp + fn || 1);
  const specificity = tn / (tn + fp || 1);

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Target className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">Holdout Confusion Matrix</h4>
            <p className="text-xs text-slate-400">Diagnostic error distribution on unseen validation instances</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            Accuracy: {(accuracy * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* 2x2 Grid */}
      <div className="grid grid-cols-2 gap-3">
        {/* True Negative */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30 relative overflow-hidden group hover:border-emerald-400 transition-colors">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-emerald-400 flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> True Negative (TN)
            </span>
            <span className="font-mono text-slate-500">{((tn / total) * 100).toFixed(1)}%</span>
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-2">{tn.toLocaleString()}</div>
          <p className="text-[11px] text-slate-400 mt-1">Correctly rejected negative cases</p>
        </div>

        {/* False Positive */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-rose-500/30 relative overflow-hidden group hover:border-rose-400 transition-colors">
          <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-bl-full pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-rose-400 flex items-center gap-1">
              <XCircle className="w-3.5 h-3.5" /> False Positive (FP)
            </span>
            <span className="font-mono text-slate-500">{((fp / total) * 100).toFixed(1)}%</span>
          </div>
          <div className="text-2xl font-bold font-mono text-rose-300 mt-2">{fp.toLocaleString()}</div>
          <p className="text-[11px] text-slate-400 mt-1">Type I error (False alarms)</p>
        </div>

        {/* False Negative */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-amber-500/30 relative overflow-hidden group hover:border-amber-400 transition-colors">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-bl-full pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-amber-400 flex items-center gap-1">
              <XCircle className="w-3.5 h-3.5" /> False Negative (FN)
            </span>
            <span className="font-mono text-slate-500">{((fn / total) * 100).toFixed(1)}%</span>
          </div>
          <div className="text-2xl font-bold font-mono text-amber-300 mt-2">{fn.toLocaleString()}</div>
          <p className="text-[11px] text-slate-400 mt-1">Type II error (Missed opportunities)</p>
        </div>

        {/* True Positive */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-indigo-500/40 relative overflow-hidden group hover:border-indigo-400 transition-colors">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-bl-full pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-indigo-400 flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" /> True Positive (TP)
            </span>
            <span className="font-mono text-slate-500">{((tp / total) * 100).toFixed(1)}%</span>
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-2">{tp.toLocaleString()}</div>
          <p className="text-[11px] text-slate-400 mt-1">Correctly identified positive instances</p>
        </div>
      </div>

      {/* Metric Breakdown Badges */}
      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800">
        <div className="p-2.5 rounded-lg bg-slate-900/50 text-center">
          <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Precision</div>
          <div className="text-sm font-mono font-bold text-cyan-300 mt-0.5">{(precision * 100).toFixed(1)}%</div>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/50 text-center">
          <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Recall (Sens.)</div>
          <div className="text-sm font-mono font-bold text-indigo-300 mt-0.5">{(recall * 100).toFixed(1)}%</div>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/50 text-center">
          <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Specificity</div>
          <div className="text-sm font-mono font-bold text-emerald-300 mt-0.5">{(specificity * 100).toFixed(1)}%</div>
        </div>
      </div>
    </div>
  );
};
