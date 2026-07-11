import React, { useState, useEffect } from 'react';
import { AgentPipeline } from './AgentPipeline';
import { CampaignHistory } from './CampaignHistory';
import { Server, Activity, Database, Zap } from 'lucide-react';
import type { TaskResponse } from '../types';

interface LiveOrchestrationProps {
  status: TaskResponse | null;
  isLoading: boolean;
  error: string | null;
}

export const LiveOrchestration: React.FC<LiveOrchestrationProps> = ({ status, isLoading, error }) => {
  const progress = status?.progress ?? 0;
  const isRunning = status?.status === 'in_progress' || status?.status === 'pending';
  
  // Simulated token counter
  const [tokens, setTokens] = useState(0);

  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        setTokens(prev => prev + Math.floor(Math.random() * 50) + 10);
      }, 500);
      return () => clearInterval(interval);
    }
  }, [isRunning]);

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto w-full p-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div>
          <h2 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Live AI Orchestration</h2>
          <p className="text-sm text-slate-500 mt-1">Multi-agent DAG execution and inference monitoring</p>
        </div>
        {isRunning && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-xs font-bold text-blue-500 uppercase tracking-widest font-mono">Executing</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Col: Pipeline */}
        <div className="lg:col-span-2 space-y-6">
          {/* Main Progress */}
          <div className="glass-panel p-5 rounded-2xl border border-[var(--border-main)]">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-widest">Pipeline Status</span>
              <span className="text-sm font-black text-primary font-mono">{progress}%</span>
            </div>
            <div className="h-2 bg-slate-100 dark:bg-slate-800/50 rounded-full overflow-hidden shadow-inner">
              <div 
                className="h-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-1000 ease-out relative"
                style={{ width: `${progress}%` }}
              >
                <div className="absolute inset-0 shimmer" />
              </div>
            </div>
            {status?.message && (
              <p className="text-[10px] text-slate-500 font-mono mt-3 truncate">{status.message}</p>
            )}
          </div>

          {/* Pipeline */}
          <AgentPipeline status={status} isLoading={isLoading} error={error} />
        </div>

        {/* Right Col: AI Engine Info & History */}
        <div className="space-y-6">
          {/* AI Engine Card */}
          <div className="glass-panel p-5 rounded-2xl border border-[var(--border-main)] bg-gradient-to-br from-slate-50 to-white dark:from-[#0f1117] dark:to-[#161B22]">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-200 dark:border-gray-800">
              <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Zap size={16} className="text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">AdPilot Engine</h3>
                <p className="text-[9px] text-slate-500 font-mono uppercase tracking-widest">Active Model Config</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <Server size={14} />
                  <span className="text-xs">Provider</span>
                </div>
                <span className="text-xs font-bold text-slate-900 dark:text-white">OpenRouter</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <Activity size={14} />
                  <span className="text-xs">Current Model</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded border border-primary/20 bg-primary/5 text-primary font-bold">Claude 3.5 Sonnet</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                  <Database size={14} />
                  <span className="text-xs">Tokens Used</span>
                </div>
                <span className="text-xs font-mono font-bold text-slate-900 dark:text-emerald-400">{tokens.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Campaign History Placeholder */}
          <CampaignHistory />
        </div>

      </div>
    </div>
  );
};
