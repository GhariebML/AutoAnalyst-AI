import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  accentColor?: 'indigo' | 'cyan' | 'emerald' | 'amber' | 'purple' | 'rose';
  tooltip?: string;
  badge?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  trend,
  accentColor = 'indigo',
  badge,
  onClick,
}) => {
  const colorMap = {
    indigo: {
      border: 'hover:border-indigo-500/40',
      iconBg: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
      glow: 'shadow-glow-indigo',
      badgeBg: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
      valColor: 'text-white',
    },
    cyan: {
      border: 'hover:border-cyan-500/40',
      iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      glow: 'shadow-glow-cyan',
      badgeBg: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
      valColor: 'text-white',
    },
    emerald: {
      border: 'hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      glow: 'shadow-glow-emerald',
      badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      valColor: 'text-emerald-300',
    },
    amber: {
      border: 'hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      glow: 'shadow-glow-amber',
      badgeBg: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
      valColor: 'text-amber-300',
    },
    purple: {
      border: 'hover:border-purple-500/40',
      iconBg: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      glow: 'shadow-glow-purple',
      badgeBg: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
      valColor: 'text-purple-300',
    },
    rose: {
      border: 'hover:border-rose-500/40',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      glow: 'shadow-glow-rose',
      badgeBg: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
      valColor: 'text-rose-300',
    },
  };

  const scheme = colorMap[accentColor];

  return (
    <div
      onClick={onClick}
      className={`glass-panel glass-card-hover p-5 rounded-3xl border border-slate-800/90 ${scheme.border} flex flex-col justify-between space-y-3 transition-all ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className={`p-2 rounded-xl border ${scheme.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="space-y-1">
        <div className="flex items-baseline justify-between gap-2">
          <div className={`text-2xl font-extrabold font-mono tracking-tight ${scheme.valColor}`}>
            {value}
          </div>

          {trend && (
            <div
              className={`flex items-center gap-1 text-[11px] font-semibold ${
                trend.isPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {trend.isPositive ? (
                <TrendingUp className="w-3.5 h-3.5" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5" />
              )}
              <span>{trend.value}</span>
            </div>
          )}

          {badge && (
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${scheme.badgeBg}`}
            >
              {badge}
            </span>
          )}
        </div>

        {subtext && <p className="text-[11px] text-slate-400 leading-relaxed">{subtext}</p>}
      </div>
    </div>
  );
};
