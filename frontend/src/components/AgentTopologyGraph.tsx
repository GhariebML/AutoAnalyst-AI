import React, { useState } from 'react';
import {
  Search,
  BarChart3,
  Wrench,
  Cpu,
  Award,
  FileText,
  CheckCircle2,
  Clock,
  ShieldAlert,
  ChevronRight,
  Sparkles,
  Info,
} from 'lucide-react';
import { AgentTelemetry } from '../types';

interface AgentNode {
  id: string;
  name: string;
  shortName: string;
  role: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  glowColor: string;
  description: string;
  capabilities: string[];
}

const AGENT_NODES: AgentNode[] = [
  {
    id: 'profiling_agent',
    name: 'Data Profiling Agent',
    shortName: 'Profiling',
    role: 'Audit schema, health score & missingness',
    icon: Search,
    color: 'text-cyan-400',
    glowColor: 'rgba(6, 182, 212, 0.4)',
    description: 'Inspects raw dataset dimensions, column data types, computes composite quality health score (0-100%), and flags data hygiene gaps.',
    capabilities: ['profile_dataset', 'audit_data_quality', 'detect_missingness'],
  },
  {
    id: 'eda_agent',
    name: 'Exploratory Data Analysis Agent',
    shortName: 'EDA',
    role: 'Correlations, distribution shapes & outliers',
    icon: BarChart3,
    color: 'text-purple-400',
    glowColor: 'rgba(192, 132, 252, 0.4)',
    description: 'Computes Pearson & Spearman correlation matrices, classifies empirical distributions (Gaussian, skewed, uniform), and identifies statistical outliers.',
    capabilities: ['compute_correlations', 'analyze_distributions', 'detect_outliers'],
  },
  {
    id: 'preprocessing_agent',
    name: 'Preprocessing Agent',
    shortName: 'Preprocessing (HITL)',
    role: 'Adaptive cleaning, Winsorization & encoding',
    icon: Wrench,
    color: 'text-amber-400',
    glowColor: 'rgba(245, 158, 11, 0.4)',
    description: 'Generates transformation plans, enforces Human-in-the-Loop review for severe missingness (>15%), applies median/mean imputation, and encodes categoricals.',
    capabilities: ['plan_transformations', 'clean_dataset', 'encode_features', 'request_hitl_approval'],
  },
  {
    id: 'ml_agent',
    name: 'Machine Learning Agent',
    shortName: 'ML Modeling',
    role: 'Task detection, candidate zoo benchmarking',
    icon: Cpu,
    color: 'text-indigo-400',
    glowColor: 'rgba(99, 102, 241, 0.4)',
    description: 'Infers classification vs. regression tasks, trains and benchmarks a candidate model zoo with stratified cross-validation, and declares the champion algorithm.',
    capabilities: ['infer_task_type', 'benchmark_models', 'train_champion_model'],
  },
  {
    id: 'evaluation_agent',
    name: 'Evaluation & Diagnostics Agent',
    shortName: 'Diagnostics',
    role: 'Holdout testing, confusion matrix & feature impact',
    icon: Award,
    color: 'text-emerald-400',
    glowColor: 'rgba(16, 185, 129, 0.4)',
    description: 'Generates holdout diagnostic metrics (ROC-AUC, RMSE, F1), analyzes confusion matrix quadrants, checks residual homoscedasticity, and ranks feature drivers.',
    capabilities: ['evaluate_champion', 'optimize_threshold', 'compute_permutation_importance'],
  },
  {
    id: 'reporting_agent',
    name: 'Reporting & Strategy Agent',
    shortName: 'Reporting',
    role: 'Multi-agent synthesis, drift & executive report',
    icon: FileText,
    color: 'text-sky-400',
    glowColor: 'rgba(56, 189, 248, 0.4)',
    description: 'Synthesizes findings across all 5 predecessor agents, checks distribution drift against historical runs, and compiles executive standalone reports.',
    capabilities: ['synthesize_insights', 'compile_reports', 'monitor_drift'],
  },
];

interface AgentTopologyGraphProps {
  currentAgent: string | null;
  agentTelemetry: Record<string, AgentTelemetry>;
  isRunning: boolean;
  status: string;
}

export const AgentTopologyGraph: React.FC<AgentTopologyGraphProps> = ({
  currentAgent,
  agentTelemetry,
  isRunning,
  status,
}) => {
  const [selectedAgent, setSelectedAgent] = useState<AgentNode | null>(null);

  const getAgentStatus = (agentId: string) => {
    if (status === 'paused_hitl' && currentAgent === agentId) return 'hitl';
    if (isRunning && currentAgent === agentId) return 'active';
    if (agentTelemetry[agentId]?.status === 'completed') return 'completed';
    if (agentTelemetry[agentId]?.status === 'error') return 'error';
    return 'idle';
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 relative overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white tracking-wide">Multi-Agent Autonomous Topology</h4>
            <p className="text-xs text-slate-400">Live dynamic routing, backtrack recovery & tool capability graph</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1 text-slate-400 bg-slate-900/60 px-2.5 py-1 rounded-full border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Completed
          </span>
          <span className="flex items-center gap-1 text-slate-400 bg-slate-900/60 px-2.5 py-1 rounded-full border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping"></span> Active
          </span>
          <span className="flex items-center gap-1 text-slate-400 bg-slate-900/60 px-2.5 py-1 rounded-full border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span> HITL Gate
          </span>
        </div>
      </div>

      {/* Interactive Node Flow Graph */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
        {AGENT_NODES.map((node, index) => {
          const nodeStatus = getAgentStatus(node.id);
          const telemetry = agentTelemetry[node.id];
          const Icon = node.icon;
          const isSelected = selectedAgent?.id === node.id;

          let statusBadge = (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
              Idle
            </span>
          );

          if (nodeStatus === 'active') {
            statusBadge = (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/50 animate-pulse flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span> Active
              </span>
            );
          } else if (nodeStatus === 'completed') {
            statusBadge = (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Done
              </span>
            );
          } else if (nodeStatus === 'hitl') {
            statusBadge = (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/50 animate-bounce flex items-center gap-1">
                <ShieldAlert className="w-3 h-3" /> HITL
              </span>
            );
          }

          return (
            <div
              key={node.id}
              onClick={() => setSelectedAgent(isSelected ? null : node)}
              className={`p-3.5 rounded-xl transition-all duration-300 cursor-pointer flex flex-col justify-between relative group ${
                isSelected
                  ? 'bg-slate-800 ring-2 ring-indigo-400 shadow-glow-indigo'
                  : nodeStatus === 'active'
                  ? 'bg-slate-800/90 ring-1 ring-indigo-500/80 shadow-glow-indigo'
                  : nodeStatus === 'completed'
                  ? 'bg-slate-900/80 border border-emerald-500/30 hover:border-emerald-400'
                  : 'bg-slate-900/50 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/50'
              }`}
            >
              {/* Connection step pill */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold text-slate-500 bg-slate-800/80 px-1.5 py-0.5 rounded">
                  0{index + 1}
                </span>
                {statusBadge}
              </div>

              {/* Node Icon & Name */}
              <div className="space-y-1.5 my-1">
                <div className="flex items-center gap-2">
                  <div
                    className={`p-2 rounded-lg ${
                      nodeStatus === 'active' ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs font-bold text-white truncate">{node.shortName}</span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-snug">{node.role}</p>
              </div>

              {/* Telemetry Footer */}
              <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
                <span className="flex items-center gap-1 font-mono">
                  <Clock className="w-3 h-3 text-slate-500" />
                  {telemetry ? `${(telemetry.duration_ms / 1000).toFixed(1)}s` : '--'}
                </span>
                <span className="text-indigo-400 flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
                  Inspect <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Agent Persona Drawer */}
      {selectedAgent && (
        <div className="mt-4 p-4 rounded-xl bg-slate-900/90 border border-indigo-500/40 animate-fadeIn space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                <selectedAgent.icon className="w-5 h-5" />
              </div>
              <div>
                <h5 className="text-sm font-bold text-white">{selectedAgent.name}</h5>
                <p className="text-xs text-indigo-300 font-mono">ID: {selectedAgent.id}</p>
              </div>
            </div>
            <button
              onClick={() => setSelectedAgent(null)}
              className="text-xs text-slate-400 hover:text-white px-2 py-1 rounded bg-slate-800"
            >
              Close
            </button>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">{selectedAgent.description}</p>

          <div>
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
              <Info className="w-3 h-3 text-cyan-400" /> Autonomous Capabilities & Tools
            </div>
            <div className="flex flex-wrap gap-1.5">
              {selectedAgent.capabilities.map((cap) => (
                <span
                  key={cap}
                  className="px-2.5 py-1 rounded-md text-[11px] font-mono bg-slate-800 text-cyan-300 border border-cyan-500/20"
                >
                  ⚡ {cap}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
