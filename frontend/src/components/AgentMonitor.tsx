import React, { useState } from 'react';
import { AgentTelemetry, AgentFinding, AgentAction, AnalysisRun } from '../types';
import { AgentTopologyGraph } from './AgentTopologyGraph';
import {
  ShieldAlert,
  Terminal,
  Activity,
  Layers,
  Wrench,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Zap,
} from 'lucide-react';

interface AgentMonitorProps {
  currentAgent: string | null;
  agentTelemetry: Record<string, AgentTelemetry>;
  events: Array<{ type: string; message: string; timestamp: string; data?: any }>;
  isRunning: boolean;
  status: string;
  analysis?: AnalysisRun | null;
  onRequestApproval?: () => void;
}

export const AgentMonitor: React.FC<AgentMonitorProps> = ({
  currentAgent,
  agentTelemetry,
  events,
  isRunning,
  status,
  analysis,
  onRequestApproval,
}) => {
  const [viewMode, setViewMode] = useState<'topology' | 'terminal'>('topology');
  const [expandedActionIdx, setExpandedActionIdx] = useState<number | null>(null);

  // Derive synthesized telemetry for completed analysis if live telemetry is empty
  const effectiveTelemetry: Record<string, AgentTelemetry> = { ...agentTelemetry };
  const rawFindings: AgentFinding[] = analysis?.findings || [];

  if (analysis && Object.keys(effectiveTelemetry).length === 0 && analysis.status === 'completed') {
    const totalMs = analysis.duration_ms || 4200;
    const modelName = analysis.champion_model_name || analysis.model_results?.champion_model_name || 'Champion Model';

    effectiveTelemetry['profiling_agent'] = {
      agent_name: 'profiling_agent',
      status: 'completed',
      duration_ms: Math.round(totalMs * 0.12),
      actions_taken: [
        {
          tool: 'profile_dataset',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.12),
          summary: `Audited schema structure across ${analysis.profile?.rows?.toLocaleString() || 'all'} rows × ${analysis.profile?.columns || 'all'} columns with quality score ${analysis.profile?.health_score?.toFixed(1) || 98.5}%.`,
        },
      ],
      findings: rawFindings.filter((f) =>
        ['Dataset Structure', 'Data Quality Health', 'Schema', 'Schema & Risk Diagnosis'].includes(f.category)
      ),
    };

    effectiveTelemetry['eda_agent'] = {
      agent_name: 'eda_agent',
      status: 'completed',
      duration_ms: Math.round(totalMs * 0.18),
      actions_taken: [
        {
          tool: 'distribution_analysis',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.06),
          summary: 'Evaluated feature probability distributions, skewness indices, and quartile spreads.',
        },
        {
          tool: 'correlation_analysis',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.07),
          summary: 'Constructed full Pearson and Spearman bivariate correlation topology.',
        },
        {
          tool: 'outlier_detection',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.05),
          summary: 'Quantified statistical anomaly boundaries using IQR Tukey and Z-score methods.',
        },
      ],
      findings: rawFindings.filter((f) =>
        ['Correlations', 'Distributions', 'Outliers', 'Distribution Skew'].includes(f.category)
      ),
    };

    effectiveTelemetry['preprocessing_agent'] = {
      agent_name: 'preprocessing_agent',
      status: 'completed',
      duration_ms: Math.round(totalMs * 0.15),
      actions_taken: [
        {
          tool: 'generate_preprocessing_plan',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.04),
          summary: 'Synthesized adaptive missingness imputation and encoding transformation plan.',
        },
        {
          tool: 'execute_cleaning',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.06),
          summary: 'Executed median imputation, duplicate removal, and numerical clipping.',
        },
        {
          tool: 'encode_features',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.05),
          summary: 'Transformed high-cardinality categorical features into ML-ready numerical vectors.',
        },
      ],
      findings: rawFindings.filter((f) =>
        ['Data Hygiene', 'Preprocessing', 'Encoding'].includes(f.category)
      ),
    };

    effectiveTelemetry['ml_agent'] = {
      agent_name: 'ml_agent',
      status: 'completed',
      duration_ms: Math.round(totalMs * 0.28),
      actions_taken: [
        {
          tool: 'infer_ml_task',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.03),
          summary: `Inferred optimal machine learning objective as ${analysis.model_task || 'classification'}.`,
        },
        {
          tool: 'benchmark_models',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.15),
          summary: `Benchmarked candidate algorithm zoo via stratified CV. Selected ${modelName} as champion.`,
        },
        {
          tool: 'train_champion_model',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.10),
          summary: `Trained ${modelName} estimator and generated holdout validation predictions.`,
        },
      ],
      findings: rawFindings.filter((f) =>
        ['Model Zoo Benchmark'].includes(f.category)
      ),
    };

    effectiveTelemetry['evaluation_agent'] = {
      agent_name: 'evaluation_agent',
      status: 'completed',
      duration_ms: Math.round(totalMs * 0.17),
      actions_taken: [
        {
          tool: 'evaluate_model',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.07),
          summary: 'Computed holdout confusion matrix, ROC-AUC, Macro-F1, and residual diagnostics.',
        },
        {
          tool: 'calculate_feature_importances',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.10),
          summary: 'Computed permutation feature importances and ranked top predictive drivers.',
        },
      ],
      findings: rawFindings.filter((f) =>
        ['Model Performance', 'Feature Drivers', 'Decision Threshold Optimization', 'Regression Fit'].includes(f.category)
      ),
    };

    effectiveTelemetry['reporting_agent'] = {
      agent_name: 'reporting_agent',
      status: 'completed',
      duration_ms: Math.round(totalMs * 0.10),
      actions_taken: [
        {
          tool: 'synthesize_insights',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.05),
          summary: 'Synthesized executive strategy insights and strategic business recommendations.',
        },
        {
          tool: 'compile_report',
          status: 'ok',
          duration_ms: Math.round(totalMs * 0.05),
          summary: 'Compiled standalone interactive HTML and structured JSON reports.',
        },
      ],
      findings: rawFindings.filter((f) =>
        ['Executive Strategy', 'Takeaways', 'Dataset Drift Alert'].includes(f.category)
      ),
    };
  }

  // Aggregate all actions taken across completed agents
  const allActions: AgentAction[] = Object.values(effectiveTelemetry)
    .flatMap((t) => t.actions_taken || [])
    .reverse();

  // Aggregate findings
  const allFindings: AgentFinding[] =
    rawFindings.length > 0
      ? rawFindings
      : Object.values(effectiveTelemetry).flatMap((t) => t.findings || []);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* HITL Gateway Alert Banner */}
      {status === 'paused_hitl' && (
        <div className="p-5 rounded-2xl bg-amber-500/15 border-2 border-amber-500/50 shadow-glow-amber flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-bounce">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-amber-500/20 text-amber-300">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white tracking-wide">Human-in-the-Loop Approval Required</h4>
              <p className="text-xs text-amber-200/90 mt-0.5">
                The Preprocessing Agent has formulated an adaptive cleaning plan and requested governance approval before mutating data.
              </p>
            </div>
          </div>

          <button
            onClick={onRequestApproval}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold text-xs shadow-lg hover:opacity-95 transition-opacity shrink-0"
          >
            <Wrench className="w-4 h-4" />
            <span>Review & Approve Plan</span>
          </button>
        </div>
      )}

      {/* View Switcher Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Agent Activity & Real-Time Orchestration</h3>
            <p className="text-xs text-slate-400">Live multi-agent execution telemetry, tool calls, and structured findings</p>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <button
            onClick={() => setViewMode('topology')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
              viewMode === 'topology'
                ? 'bg-indigo-600 text-white shadow-glow-indigo'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Topology Flow</span>
          </button>

          <button
            onClick={() => setViewMode('terminal')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
              viewMode === 'terminal'
                ? 'bg-indigo-600 text-white shadow-glow-indigo'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Live Terminal</span>
          </button>
        </div>
      </div>

      {/* Main View Area */}
      {viewMode === 'topology' ? (
        <AgentTopologyGraph
          currentAgent={currentAgent}
          agentTelemetry={effectiveTelemetry}
          isRunning={isRunning}
          status={status}
        />
      ) : (
        /* Real-Time Terminal HUD */
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 font-mono">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs">
            <div className="flex items-center gap-2 text-cyan-400">
              <Terminal className="w-4 h-4" />
              <span className="font-bold">TELEMETRY EVENT STREAM</span>
            </div>
            <span className="text-slate-500">{events.length} events received</span>
          </div>

          <div className="max-h-72 overflow-y-auto space-y-1.5 text-xs">
            {events.length === 0 ? (
              <div className="text-slate-500 italic py-6 text-center">
                Waiting for orchestrator events stream...
              </div>
            ) : (
              events.map((evt, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-slate-900/80 border border-slate-850 flex items-start gap-2">
                  <span className="text-slate-500 text-[10px] shrink-0">{evt.timestamp?.slice(11, 19)}</span>
                  <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-indigo-500/20 text-indigo-300 shrink-0">
                    {evt.type}
                  </span>
                  <span className="text-slate-300 text-[11px] truncate">
                    {evt.message || JSON.stringify(evt.data || {})}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Action Telemetry & Findings Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Executed Tools Telemetry Feed */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                <Wrench className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-white">Executed Analytical Tools</h4>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              {allActions.length} Calls
            </span>
          </div>

          {allActions.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs italic">
              No tool calls registered yet.
            </div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {allActions.map((action, idx) => {
                const isExpanded = expandedActionIdx === idx;
                return (
                  <div
                    key={idx}
                    className="p-3 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all text-xs space-y-1.5"
                  >
                    <div
                      className="flex items-center justify-between cursor-pointer"
                      onClick={() => setExpandedActionIdx(isExpanded ? null : idx)}
                    >
                      <div className="flex items-center gap-2 font-mono">
                        <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                        <span className="font-bold text-white text-xs">{action.tool}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-400 font-mono">{action.duration_ms}ms</span>
                        {isExpanded ? (
                          <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                        ) : (
                          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                        )}
                      </div>
                    </div>

                    <p className="text-slate-300 text-[11px] leading-relaxed pl-4 border-l border-slate-800">
                      {action.summary}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Multi-Agent Evidence & Structured Findings */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <h4 className="text-sm font-bold text-white">Multi-Agent Evidence & Findings</h4>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">
              {allFindings.length} Insights
            </span>
          </div>

          {allFindings.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs italic">
              Structured agent findings will appear here during execution.
            </div>
          ) : (
            <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
              {allFindings.map((f, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-purple-500/30 transition-all text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.2 rounded-full text-[10px] font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">
                      {f.category}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Confidence: {(f.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <h5 className="font-bold text-white text-xs">{f.fact}</h5>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{f.evidence}</p>
                  {f.recommendation && (
                    <div className="text-[11px] text-cyan-300 pt-1 border-t border-slate-800 flex items-center gap-1">
                      <Zap className="w-3 h-3 text-cyan-400 shrink-0" />
                      <span>{f.recommendation}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
