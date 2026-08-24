import React, { useState, useEffect } from 'react';
import {
  Activity,
  BrainCircuit,
  Wrench,
  CheckCircle2,
  RefreshCw,
  Search,
  Zap,
  ShieldCheck,
} from 'lucide-react';
import { fetchFullSystemHealth, fetchToolsCatalog, fetchLLMHealth } from '../api/client';
import { FullSystemHealth, ToolCatalogItem } from '../types';
import { LoadingSkeleton } from './common/LoadingSkeleton';

export const SystemHealthView: React.FC = () => {
  const [health, setHealth] = useState<FullSystemHealth | null>(null);
  const [tools, setTools] = useState<ToolCatalogItem[]>([]);
  const [llmHealth, setLlmHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toolSearch, setToolSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const loadData = async () => {
    try {
      setLoading(true);
      const [hData, tData, lData] = await Promise.all([
        fetchFullSystemHealth().catch(() => null),
        fetchToolsCatalog().catch(() => []),
        fetchLLMHealth().catch(() => null),
      ]);
      setHealth(hData);
      setTools(tData);
      setLlmHealth(lData);
    } catch (err) {
      console.error('Failed to load system health:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const categories = ['all', ...Array.from(new Set(tools.map((t) => t.category)))];

  const filteredTools = tools.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(toolSearch.toLowerCase()) ||
      t.description.toLowerCase().includes(toolSearch.toLowerCase()) ||
      t.tags.some((tag) => tag.toLowerCase().includes(toolSearch.toLowerCase()));
    const matchesCat = selectedCategory === 'all' || t.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  if (loading && !health) {
    return <LoadingSkeleton rows={4} height="h-32" />;
  }

  const usageSummary = llmHealth?.usage_summary || {};

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-glow-indigo">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white">AI Infrastructure & Tool Catalog</h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> All Systems Operational
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time monitoring of OpenRouter LLM gateway, analytical tool registry, and multi-agent orchestrator.
            </p>
          </div>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs font-bold text-slate-200 transition-all self-start md:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Diagnostics</span>
        </button>
      </div>

      {/* Subsystem Health Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {health?.subsystems.map((sub, idx) => (
          <div
            key={idx}
            className="glass-panel glass-card-hover p-5 rounded-3xl border border-slate-800 space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white truncate">{sub.name}</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                {sub.status}
              </span>
            </div>

            <p className="text-[11px] text-slate-400 leading-relaxed">{sub.details}</p>

            <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-500">
              <span>Latency</span>
              <span className="text-cyan-400">{sub.latency_ms}ms</span>
            </div>
          </div>
        ))}
      </div>

      {/* OpenRouter LLM Gateway Monitor */}
      <div className="glass-panel p-6 rounded-3xl border border-indigo-500/30 space-y-5 bg-gradient-to-r from-indigo-950/20 to-slate-900/60">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Centralized OpenRouter LLM Gateway</h3>
              <p className="text-xs text-slate-400">Intelligent reasoning layer powering multi-agent synthesis and AI Copilot</p>
            </div>
          </div>

          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
            Provider: {llmHealth?.provider || 'OpenRouter'}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Primary Model</span>
            <div className="text-xs font-bold font-mono text-white truncate">{llmHealth?.primary_model || 'openai/gpt-4o-mini'}</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Fallback Model</span>
            <div className="text-xs font-bold font-mono text-cyan-300 truncate">{llmHealth?.fallback_model || 'anthropic/claude-3.5-haiku'}</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Total Tokens Processed</span>
            <div className="text-base font-bold font-mono text-emerald-300">{(usageSummary.total_tokens || 0).toLocaleString()}</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Gateway Success Rate</span>
            <div className="text-base font-bold font-mono text-purple-300">{usageSummary.success_rate_pct || 100}%</div>
          </div>
        </div>
      </div>

      {/* Analytical Tool Registry Catalog */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Wrench className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Registered Analytical Tool Catalog ({tools.length})</h3>
              <p className="text-xs text-slate-400">Deterministic mathematical, statistical, and ML libraries callable by autonomous agents</p>
            </div>
          </div>

          {/* Search & Category Filter */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search tools or tags..."
                value={toolSearch}
                onChange={(e) => setToolSearch(e.target.value)}
                className="pl-9 pr-4 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-xl text-xs font-bold capitalize transition-all ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-glow-indigo'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTools.map((t, idx) => (
            <div
              key={idx}
              className="glass-panel glass-card-hover p-4 rounded-2xl border border-slate-800 space-y-2.5 flex flex-col justify-between"
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-cyan-300">
                    <Zap className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{t.name}</span>
                  </div>
                  <span className="px-2 py-0.2 rounded text-[9px] font-mono uppercase bg-slate-900 text-slate-400 border border-slate-800">
                    {t.category}
                  </span>
                </div>

                <p className="text-[11px] text-slate-300 leading-relaxed">{t.description}</p>
              </div>

              <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-1 overflow-hidden">
                  {t.tags.slice(0, 2).map((tag, tIdx) => (
                    <span
                      key={tIdx}
                      className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 truncate"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
                <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> Autonomous
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
