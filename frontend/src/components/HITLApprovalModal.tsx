import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Wrench,
  Sparkles,
  AlertTriangle,
  Zap,
} from 'lucide-react';

interface HITLApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  runId: string;
  humanPrompt: string | null;
  onApprove: (approved: boolean, modifications?: Record<string, any>) => void;
}

export const HITLApprovalModal: React.FC<HITLApprovalModalProps> = ({
  isOpen,
  onClose,
  runId,
  humanPrompt,
  onApprove,
}) => {
  const [strategy, setStrategy] = useState<'recommended' | 'conservative' | 'aggressive'>('recommended');
  const [customNotes, setCustomNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleConfirm = async (approved: boolean) => {
    setIsSubmitting(true);
    try {
      await onApprove(approved, {
        strategy,
        custom_notes: customNotes,
        approved_at: new Date().toISOString(),
      });
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-lg animate-fadeIn">
      <div className="w-full max-w-2xl glass-panel rounded-3xl border-2 border-amber-500/50 shadow-glow-amber overflow-hidden space-y-6 p-6 sm:p-8 animate-scaleUp">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-white">Human-in-the-Loop Governance Gate</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300">
                  PAUSED
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Run #{runId.slice(0, 8)} • Preprocessing Agent</p>
            </div>
          </div>
        </div>

        {/* Prompt Card */}
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-2 text-xs">
          <div className="text-slate-400 font-semibold flex items-center gap-1.5 text-amber-300">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Agent Reason for Governance Pause:</span>
          </div>
          <p className="text-slate-200 leading-relaxed font-mono">
            {humanPrompt ||
              'High missingness or critical data quality thresholds encountered. Please review and confirm the proposed transformation plan before execution.'}
          </p>
        </div>

        {/* Strategy Presets */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Choose Execution Strategy Preset:
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div
              onClick={() => setStrategy('recommended')}
              className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
                strategy === 'recommended'
                  ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-glow-indigo'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span>Adaptive (Auto)</span>
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                Median for skewed numerics, mode for categoricals, 1.5x IQR Winsorization.
              </p>
            </div>

            <div
              onClick={() => setStrategy('conservative')}
              className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
                strategy === 'conservative'
                  ? 'bg-emerald-600/20 border-emerald-500 text-white shadow-glow-emerald'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span>Conservative</span>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                Impute only &lt; 5% missing, keep duplicates, preserve raw outliers.
              </p>
            </div>

            <div
              onClick={() => setStrategy('aggressive')}
              className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
                strategy === 'aggressive'
                  ? 'bg-amber-600/20 border-amber-500 text-white shadow-glow-amber'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span>Aggressive Clean</span>
                <Zap className="w-3.5 h-3.5 text-amber-400" />
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                Drop columns &gt; 40% missing, 3.0x Z-score cap, one-hot encode all.
              </p>
            </div>
          </div>
        </div>

        {/* Custom Governance Notes */}
        <div className="space-y-1.5 text-xs">
          <label className="text-slate-400 font-semibold">Governance / Override Notes (Optional):</label>
          <input
            type="text"
            placeholder="e.g., Approved with caveat to monitor column X after encoding..."
            value={customNotes}
            onChange={(e) => setCustomNotes(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-amber-400 font-mono"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <button
            onClick={() => handleConfirm(false)}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-semibold transition-colors"
          >
            <XCircle className="w-4 h-4 text-rose-400" />
            <span>Reject & Abort Run</span>
          </button>

          <button
            onClick={() => handleConfirm(true)}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold text-xs shadow-glow-amber hover:opacity-95 transition-opacity"
          >
            <Wrench className="w-4 h-4" />
            <span>{isSubmitting ? 'Resuming Orchestrator...' : 'Approve & Resume Pipeline'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
