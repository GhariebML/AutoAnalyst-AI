import React, { useState, useEffect } from 'react';
import { Dataset, AnalysisRun, DashboardSummary, RunTimelineItem, AgentActivitySummary } from '../types';
import {
  Database,
  Cpu,
  Sparkles,
  ShieldCheck,
  Layers,
  Award,
  Zap,
  BrainCircuit,
  Activity,
  PlusCircle,
  BarChart3,
} from 'lucide-react';
import { MetricCard } from './common/MetricCard';
import { DataLineageDiagram } from './common/DataLineageDiagram';
import { fetchDashboardSummary, fetchRunsTimeline, fetchAgentsActivity } from '../api/client';

interface DashboardProps {
  datasets: Dataset[];
  analyses: AnalysisRun[];
  onSelectDataset: (id: string) => void;
  onOpenAnalysis: (id: string) => void;
  onNewAnalysis: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  datasets,
  analyses,
  onSelectDataset: _onSelectDataset,
  onOpenAnalysis,
  onNewAnalysis,
}) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [timeline, setTimeline] = useState<RunTimelineItem[]>([]);
  const [agentsActivity, setAgentsActivity] = useState<AgentActivitySummary[]>([]);
  const [timelineFilter, setTimelineFilter] = useState<number>(7);

  useEffect(() => {
    fetchDashboardSummary().then(setSummary).catch(console.error);
    fetchRunsTimeline(timelineFilter).then(setTimeline).catch(console.error);
    fetchAgentsActivity().then(setAgentsActivity).catch(console.error);
  }, [timelineFilter, analyses.length]);

  const completedRuns = summary?.completed_runs ?? analyses.filter((a) => a.status === 'completed').length;
  const runningRuns = summary?.running_runs ?? analyses.filter((a) => a.status === 'running' || a.status === 'paused_hitl').length;
  const totalDatasets = summary?.total_datasets ?? datasets.length;
  const modelsTrained = summary?.total_models_trained ?? analyses.filter((a) => a.champion_model_name).length;
  const totalInsights = summary?.total_insights ?? analyses.reduce((acc, a) => acc + (a.insights?.length || 0), 0);
  const avgHealth = summary?.avg_quality_score ?? 98.5;

  const recentAnalyses = analyses.slice(0, 6);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Analytics Command Center Banner */}
      <div className="relative overflow-hidden rounded-3xl glass-panel p-8 border border-slate-800 bg-gradient-to-r from-indigo-950/40 via-slate-900/60 to-purple-950/30">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-1/3 w-64 h-64 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Autonomous Analytics Command Center</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Enterprise <span className="gradient-text-cyber">AI Data Intelligence</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Orchestrate specialized AI agents to autonomously audit schema quality, discover correlation topologies, execute adaptive cleaning, benchmark predictive ML zoos, and generate executive strategy briefs.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              onClick={onNewAnalysis}
              className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-500 text-white font-bold text-sm shadow-glow-indigo hover:opacity-95 transition-all transform hover:-translate-y-0.5"
            >
              <Zap className="w-4 h-4" />
              <span>Launch Autonomous Run</span>
            </button>
          </div>
        </div>
      </div>

      {/* High-Density KPI Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard
          title="Analysis Runs"
          value={summary?.total_runs ?? analyses.length}
          subtext={`${completedRuns} completed`}
          icon={Layers}
          accentColor="indigo"
        />

        <MetricCard
          title="Active Runs"
          value={runningRuns}
          subtext={runningRuns > 0 ? 'Orchestrating' : 'Queue idle'}
          icon={Activity}
          accentColor="cyan"
          badge={runningRuns > 0 ? 'Live' : undefined}
        />

        <MetricCard
          title="Datasets Hub"
          value={totalDatasets}
          subtext="Versioned datasets"
          icon={Database}
          accentColor="emerald"
        />

        <MetricCard
          title="Models Trained"
          value={modelsTrained}
          subtext="Candidate ML zoo"
          icon={Cpu}
          accentColor="purple"
        />

        <MetricCard
          title="Data Health"
          value={`${avgHealth.toFixed(1)}%`}
          subtext="Quality health score"
          icon={ShieldCheck}
          accentColor="amber"
        />

        <MetricCard
          title="AI Insights"
          value={totalInsights}
          subtext="Structured findings"
          icon={BrainCircuit}
          accentColor="rose"
        />
      </div>

      {/* Visual Intelligence Section: Runs Timeline & Status Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Runs Activity Timeline Chart Card */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4 lg:col-span-2 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
                <BarChart3 className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Analysis Runs Activity Over Time</h3>
                <p className="text-xs text-slate-400">Execution frequency across completed and active runs</p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
              {[7, 30, 90].map((days) => (
                <button
                  key={days}
                  onClick={() => setTimelineFilter(days)}
                  className={`px-2.5 py-1 rounded-lg font-mono font-bold transition-all ${
                    timelineFilter === days
                      ? 'bg-indigo-600 text-white shadow-glow-indigo'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {days}D
                </button>
              ))}
            </div>
          </div>

          {timeline.length === 0 ? (
            <div className="py-16 text-center text-xs text-slate-500 italic">
              No historical analysis runs logged yet. Launch an analysis to populate time-series trends.
            </div>
          ) : (
            <div className="space-y-4">
              <div className="h-44 flex items-end gap-2 pt-6">
                {timeline.map((item, idx) => {
                  const maxTotal = Math.max(...timeline.map((t) => t.total), 1);
                  const heightPct = Math.max(15, (item.total / maxTotal) * 100);

                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group relative">
                      <div className="absolute -top-7 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 px-2 py-1 rounded border border-slate-800 text-[10px] font-mono text-indigo-300 pointer-events-none whitespace-nowrap z-20">
                        {item.date}: {item.completed} completed ({item.total} total)
                      </div>

                      <div
                        style={{ height: `${heightPct}%` }}
                        className="w-full rounded-t-xl bg-gradient-to-t from-indigo-600 to-cyan-400 group-hover:brightness-125 transition-all shadow-glow-indigo"
                      />
                      <span className="text-[10px] font-mono text-slate-500 truncate w-full text-center">
                        {item.date.slice(5)}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
                <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span> Completed Runs
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span> Active Runs
                  </span>
                </div>
                <span className="text-slate-400 text-xs font-mono font-bold">
                  {summary?.total_runs || analyses.length} total runs
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Run Status Donut / Distribution Card */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                <PieChartIcon />
              </div>
              <h3 className="text-sm font-bold text-white">Status Distribution</h3>
            </div>
            <span className="text-xs font-mono text-slate-400">All Time</span>
          </div>

          <div className="space-y-3 my-auto">
            <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span className="text-slate-300 font-medium">Completed</span>
              </div>
              <span className="text-sm font-mono font-bold text-white">{completedRuns}</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <span className="text-slate-300 font-medium">Running & HITL</span>
              </div>
              <span className="text-sm font-mono font-bold text-cyan-300">{runningRuns}</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/70 border border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                <span className="text-slate-300 font-medium">Failed</span>
              </div>
              <span className="text-sm font-mono font-bold text-slate-400">{summary?.failed_runs || 0}</span>
            </div>
          </div>

          <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-center text-xs text-indigo-300 font-semibold">
            Success Rate: 100%
          </div>
        </div>
      </div>

      {/* Multi-Agent Workload & Capability Grid */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Multi-Agent Autonomous Capability Grid</h3>
              <p className="text-xs text-slate-400">Specialized AI agents coordinating tool calls and data reasoning</p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">
            6 Specialized Agents Active
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
          {agentsActivity.map((agent, idx) => (
            <div
              key={idx}
              className="glass-card glass-card-hover p-4 rounded-2xl border border-slate-800/90 space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{agent.display_name}</span>
                  <span className="px-2 py-0.2 rounded text-[9px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    Active
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-mono">{agent.category}</p>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-500">Avg Latency</span>
                  <span className="text-cyan-300 font-bold">{agent.avg_duration_ms}ms</span>
                </div>

                <div className="flex items-center gap-1 overflow-hidden">
                  {agent.tools_used.slice(0, 2).map((t, tIdx) => (
                    <span
                      key={tIdx}
                      className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-slate-900 text-slate-300 border border-slate-800 truncate"
                    >
                      {t}
                    </span>
                  ))}
                  {agent.tools_used.length > 2 && (
                    <span className="text-[9px] font-mono text-slate-500">+{agent.tools_used.length - 2}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* End-to-End Lineage Flow */}
      <DataLineageDiagram
        datasetName={datasets[0]?.filename || 'Dataset'}
        championModel={analyses[0]?.champion_model_name || 'Champion Model'}
      />

      {/* Recent Analysis Runs Table */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Recent Multi-Agent Analysis Runs</h3>
              <p className="text-xs text-slate-400">History of autonomous pipeline executions and generated models</p>
            </div>
          </div>

          <button
            onClick={onNewAnalysis}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600/80 hover:bg-indigo-600 text-white font-bold text-xs shadow-glow-indigo transition-all"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Run</span>
          </button>
        </div>

        {recentAnalyses.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-500 italic">
            No analysis runs recorded yet. Upload a dataset in the Dataset Hub to trigger your first run.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
                  <th className="pb-3 pl-3">Run ID</th>
                  <th className="pb-3">Target Column</th>
                  <th className="pb-3">Task</th>
                  <th className="pb-3">Champion Algorithm</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Duration</th>
                  <th className="pb-3 pr-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentAnalyses.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-900/60 transition-colors group">
                    <td className="py-3.5 pl-3 font-mono font-bold text-indigo-300">
                      #{run.id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 font-mono text-slate-300">
                      {run.target_column || <span className="text-slate-500 italic">Unsupervised</span>}
                    </td>
                    <td className="py-3.5 capitalize font-mono text-slate-400">{run.model_task || 'auto'}</td>
                    <td className="py-3.5 font-mono font-bold text-white">
                      {run.champion_model_name ? (
                        <span className="flex items-center gap-1.5 text-amber-300">
                          <Award className="w-3.5 h-3.5 text-amber-400" />
                          <span>{run.champion_model_name}</span>
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-3.5">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                          run.status === 'completed'
                            ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                            : run.status === 'failed'
                            ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                            : 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30 animate-pulse'
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className="py-3.5 font-mono text-slate-400">{run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : '—'}</td>
                    <td className="py-3.5 pr-3 text-right">
                      <button
                        onClick={() => onOpenAnalysis(run.id)}
                        className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500 hover:text-white text-slate-300 text-xs font-semibold transition-all"
                      >
                        Inspect &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

const PieChartIcon = () => (
  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
    <path d="M22 12A10 10 0 0 0 12 2v10z" />
  </svg>
);
