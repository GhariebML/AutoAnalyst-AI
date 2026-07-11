import React from 'react';
import type { TaskResponse } from '../types';
import { 
  CheckCircle2, 
  AlertCircle, 
  Activity, 
  Cpu, 
  Network 
} from 'lucide-react';

interface CampaignProgressProps {
  status: TaskResponse | null;
  isLoading: boolean;
  error: string | null;
}

export const CampaignProgress: React.FC<CampaignProgressProps> = ({ status, isLoading, error }) => {
  if (!status && !isLoading && !error) return null;

  const getStatusIcon = () => {
    if (error) return <AlertCircle className="text-red-500 animate-pulse" size={28} />;
    if (!status) return <Activity className="text-blue-500 animate-pulse" size={28} />;
    
    switch (status.status) {
      case 'completed':
        return <CheckCircle2 className="text-teal-400" size={28} />;
      case 'failed':
        return <AlertCircle className="text-red-500" size={28} />;
      default:
        return <Cpu className="text-blue-400 animate-spin-slow" size={28} />;
    }
  };

  const getStatusText = () => {
    if (error) return 'Protocol Override Required';
    if (!status) return 'Establishing Connection...';
    switch (status.status) {
      case 'pending': return 'Mission Initialization';
      case 'in_progress': return 'Neural Processing Active';
      case 'completed': return 'Orchestration Complete';
      case 'failed': return 'Core Breach Detected';
      default: return 'Processing...';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="mission-panel p-8 relative overflow-hidden">
        {/* Animated Background Pulse */}
        <div className={`absolute inset-0 bg-primary/5 transition-opacity duration-1000 ${status?.status === 'in_progress' ? 'opacity-100' : 'opacity-0'}`}>
          <div className="absolute inset-0 animate-pulse-azure" />
        </div>

        <div className="relative z-10 flex items-center gap-6 mb-8">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border ${
              status?.status === 'completed' ? 'bg-teal-500/10 border-teal-500/30' :
              status?.status === 'failed' || error ? 'bg-red-500/10 border-red-500/30' :
              'bg-primary/10 border-primary/30'
            }`}>
              {getStatusIcon()}
            </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
                <h2 className="text-xl font-bold tracking-tight text-slate-900">{getStatusText()}</h2>
                <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Task ID: {status?.taskId?.slice(0, 8) || '####'}</span>
            </div>
              <p className="text-xs text-slate-500 font-mono flex items-center gap-2">
              <Network size={12} className={isLoading ? 'animate-pulse' : ''} />
              {status?.message || 'Awaiting transmission...'}
            </p>
          </div>
        </div>

        {/* Technical Progress Bar */}
        <div className="relative pt-2">
          <div className="flex items-center justify-between mb-3">
            <div className="flex gap-1">
              {[...Array(5)].map((_, i) => (
                <div key={i} className={`w-3 h-1 rounded-full ${i < (status?.progress || 0) / 20 ? 'bg-primary' : 'bg-gray-200'}`} />
              ))}
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-slate-900 leading-none font-mono tracking-tighter">{status?.progress || 0}</span>
              <span className="text-xs font-bold text-slate-600 font-mono">%</span>
            </div>
          </div>
          
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden border border-gray-100 shadow-inner">
            <div 
              className={`h-full transition-all duration-1000 ease-out relative ${
                status?.status === 'completed' ? 'bg-teal-500' : 
                status?.status === 'failed' ? 'bg-red-500' : 'bg-primary'
              }`}
              style={{ width: `${status?.progress || 0}%` }}
            >
              <div className="absolute inset-0 shimmer opacity-30" />
            </div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-4">
            {[
              { label: 'Latency', value: '14ms' },
              { label: 'Stability', value: '99.9%' },
              { label: 'Neural Load', value: `${(status?.progress || 0) * 0.8}%` },
            ].map((stat, i) => (
              <div key={i} className="text-center p-2 rounded-lg bg-gray-50 border border-gray-100">
                <p className="text-[8px] font-bold text-slate-500 uppercase tracking-widest mb-0.5">{stat.label}</p>
                <p className="text-[10px] font-bold text-primary font-mono">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="mt-8 p-4 bg-red-50 border border-red-100 rounded-xl">
            <div className="flex items-start gap-3">
              <AlertCircle className="text-red-600 shrink-0 mt-0.5" size={16} />
              <div>
                <p className="text-xs font-bold text-red-600 uppercase tracking-widest mb-1">Critical Error</p>
                <p className="text-xs text-red-600 leading-relaxed">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
