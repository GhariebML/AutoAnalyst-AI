import React from 'react';
import { History, ArrowUpRight, CheckCircle2 } from 'lucide-react';

export const CampaignHistory: React.FC = () => {
  const history = [
    { id: 'camp-01', name: 'Q3 Product Launch', time: '2 hours ago', status: 'success' },
    { id: 'camp-02', name: 'Holiday Sale Promo', time: '1 day ago', status: 'success' },
    { id: 'camp-03', name: 'Brand Awareness 2026', time: '3 days ago', status: 'success' },
  ];

  return (
    <div className="glass-panel p-5 rounded-2xl border border-[var(--border-main)]">
      <div className="flex items-center gap-2 mb-4">
        <History size={16} className="text-slate-400" />
        <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Recent Campaigns</h3>
      </div>
      <div className="space-y-3">
        {history.map(item => (
          <div key={item.id} className="group flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/50 cursor-pointer transition-colors border border-transparent hover:border-slate-200 dark:hover:border-slate-700/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                <CheckCircle2 size={14} className="text-emerald-500" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200">{item.name}</p>
                <p className="text-[10px] text-slate-500 font-mono mt-0.5">{item.time}</p>
              </div>
            </div>
            <ArrowUpRight size={14} className="text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        ))}
      </div>
    </div>
  );
};
