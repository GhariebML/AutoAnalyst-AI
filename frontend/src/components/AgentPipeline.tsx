import React, { useState, useEffect } from 'react';
import { Target, Search, FileText, BarChart2, Palette, CheckCircle2, Loader, Clock, ChevronDown, ChevronUp, Cpu } from 'lucide-react';
import type { TaskResponse } from '../types';

interface AgentDef {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  borderColor: string;
  range: [number, number];
  model: string;
}

const AGENTS: AgentDef[] = [
  { id: 'strategy', name: 'Strategy', description: 'Objectives & positioning', icon: Target, color: 'text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/30', range: [0, 20], model: 'Claude 3.5 Sonnet' },
  { id: 'research', name: 'Research', description: 'Market & audience data', icon: Search, color: 'text-purple-400', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/30', range: [20, 40], model: 'Claude 3.5 Sonnet' },
  { id: 'content', name: 'Content', description: 'Copy & creative assets', icon: FileText, color: 'text-teal-400', bgColor: 'bg-teal-500/10', borderColor: 'border-teal-500/30', range: [40, 60], model: 'GPT-4o' },
  { id: 'analytics', name: 'Analytics', description: 'KPIs & forecast metrics', icon: BarChart2, color: 'text-amber-400', bgColor: 'bg-amber-500/10', borderColor: 'border-amber-500/30', range: [60, 80], model: 'Claude 3.5 Sonnet' },
  { id: 'design', name: 'Design', description: 'Visual concepts & layouts', icon: Palette, color: 'text-orange-400', bgColor: 'bg-orange-500/10', borderColor: 'border-orange-500/30', range: [80, 100], model: 'Claude 3.5 Sonnet' },
];

type AgentStatus = 'idle' | 'running' | 'done' | 'error';

function getStatus(agent: AgentDef, progress: number, taskStatus: string): AgentStatus {
  if (taskStatus === 'failed' && progress > agent.range[0]) return 'error';
  if (progress >= agent.range[1]) return 'done';
  if (progress >= agent.range[0] && progress < agent.range[1]) return 'running';
  return 'idle';
}

interface AgentPipelineProps {
  status: TaskResponse | null;
  isLoading: boolean;
  error: string | null;
}

export const AgentPipeline: React.FC<AgentPipelineProps> = ({ status, error }) => {
  const progress = status?.progress ?? 0;
  const taskStatus = status?.status ?? 'pending';
  
  // Simulated runtimes for visual flair
  const [runtimes, setRuntimes] = useState<Record<string, number>>({});
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setRuntimes(prev => {
        const next = { ...prev };
        AGENTS.forEach(agent => {
          const s = getStatus(agent, progress, taskStatus);
          if (s === 'running') {
            next[agent.id] = (next[agent.id] || 0) + 1;
          }
        });
        return next;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [progress, taskStatus]);

  const formatTime = (seconds: number) => {
    if (!seconds) return '00:00';
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="space-y-4">
      {AGENTS.map((agent, idx) => {
        const s = getStatus(agent, progress, taskStatus);
        const Icon = agent.icon;
        const isExpanded = expandedAgent === agent.id;
        
        return (
          <div key={agent.id} className="relative">
            {idx < AGENTS.length - 1 && (
              <div className={`absolute left-[23px] top-[60px] w-0.5 h-6 ${s === 'done' ? 'bg-primary/40' : 'bg-gray-200 dark:bg-gray-800'}`} />
            )}
            
            <div className={`glass-panel flex flex-col rounded-xl border transition-all duration-500 overflow-hidden ${
              s === 'running' ? `${agent.bgColor} ${agent.borderColor} shadow-[0_0_20px_rgba(31,111,235,0.15)] ring-1 ring-primary/20` :
              s === 'done' ? 'bg-gray-50/50 dark:bg-[#161B22]/50 border-gray-200 dark:border-gray-800' :
              s === 'error' ? 'bg-red-50/50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30' :
              'bg-transparent border-gray-100 dark:border-gray-800/60 opacity-60'
            }`}>
              
              {/* Card Header */}
              <div 
                className="flex items-center gap-4 p-4 cursor-pointer"
                onClick={() => setExpandedAgent(isExpanded ? null : agent.id)}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border shadow-sm ${
                  s === 'done' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' :
                  s === 'running' ? `${agent.bgColor} ${agent.borderColor} ${agent.color} animate-pulse-slow` :
                  'bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-slate-400'
                }`}>
                  {s === 'done' ? <CheckCircle2 size={20} /> :
                   s === 'running' ? <Icon size={20} className="animate-bounce-subtle" /> :
                   <Icon size={20} />}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className={`text-sm font-bold ${
                      s === 'running' ? agent.color :
                      s === 'done' ? 'text-slate-900 dark:text-slate-100' : 'text-slate-600 dark:text-slate-400'
                    }`}>{agent.name} Agent</h3>
                    
                    {s === 'running' && (
                      <span className={`text-[9px] font-mono uppercase tracking-widest px-2 py-0.5 rounded-full border ${agent.bgColor} ${agent.borderColor} ${agent.color} flex items-center gap-1`}>
                        <Loader size={10} className="animate-spin" /> Processing
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-3 text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                    <span className="flex items-center gap-1">
                      <Cpu size={12} /> {agent.model}
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-600" />
                    <span className="flex items-center gap-1">
                      <Clock size={12} /> {formatTime(runtimes[agent.id] || (s === 'done' ? Math.floor(Math.random() * 15) + 5 : 0))}s
                    </span>
                  </div>
                </div>

                <div className="shrink-0 text-slate-400">
                  {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </div>
              </div>

              {/* Expanded Content (Simulated terminal logs) */}
              {isExpanded && (
                <div className="border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-[#0D0D1A]/80 p-4 font-mono text-[10px] text-slate-600 dark:text-slate-400 space-y-1.5 h-32 overflow-y-auto">
                  <p className="text-slate-500">[{formatTime(0)}] Initializing {agent.name} parameters...</p>
                  {s === 'running' && runtimes[agent.id] > 2 && <p className="text-blue-400">[{formatTime(runtimes[agent.id] - 1)}] Connecting to {agent.model}...</p>}
                  {s === 'running' && runtimes[agent.id] > 4 && <p className="text-primary animate-pulse">[{formatTime(runtimes[agent.id])}] Generating {agent.description.toLowerCase()}...</p>}
                  {s === 'done' && (
                    <>
                      <p className="text-blue-400">[{formatTime(2)}] Connected to {agent.model}</p>
                      <p className="text-emerald-500">[{formatTime(5)}] Successfully completed task: {agent.description}</p>
                      <p className="text-slate-500">[{formatTime(5)}] Output validated and passed to next stage.</p>
                    </>
                  )}
                  {s === 'idle' && <p>Awaiting previous pipeline stage completion...</p>}
                </div>
              )}
            </div>
          </div>
        );
      })}

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl mt-4">
          <p className="text-xs text-red-500 font-mono">{error}</p>
        </div>
      )}
    </div>
  );
};
