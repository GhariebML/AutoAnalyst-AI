import React, { useState, useEffect, useMemo } from 'react';
import {
  Search,
  LayoutDashboard,
  Database,
  Activity,
  BarChart3,
  Download,
  Play,
  X,
  FileCode,
  Sparkles,
} from 'lucide-react';
import { Dataset, AnalysisRun } from '../types';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (tab: 'dashboard' | 'datasets' | 'workspace' | 'analytics' | 'playground' | 'exports' | 'health') => void;
  datasets: Dataset[];
  analyses: AnalysisRun[];
  onSelectDataset: (id: string) => void;
  onOpenAnalysis: (id: string) => void;
  onTriggerQuickRun: () => void;
}

interface CommandItem {
  id: string;
  title: string;
  category: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
  shortcut?: string;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNavigate,
  datasets,
  analyses,
  onSelectDataset,
  onOpenAnalysis,
  onTriggerQuickRun,
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Close on Escape, navigate with Up/Down/Enter
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const commands = useMemo<CommandItem[]>(() => {
    const baseCommands: CommandItem[] = [
      {
        id: 'nav-dash',
        title: 'Go to Command Dashboard',
        category: 'Navigation',
        icon: LayoutDashboard,
        action: () => {
          onNavigate('dashboard');
          onClose();
        },
        shortcut: 'D',
      },
      {
        id: 'nav-data',
        title: 'Go to Dataset Ingestion Hub',
        category: 'Navigation',
        icon: Database,
        action: () => {
          onNavigate('datasets');
          onClose();
        },
        shortcut: 'U',
      },
      {
        id: 'nav-act',
        title: 'Open Agent Activity Monitor',
        category: 'Navigation',
        icon: Activity,
        action: () => {
          onNavigate('workspace');
          onClose();
        },
        shortcut: 'A',
      },
      {
        id: 'nav-ws',
        title: 'Open Interactive Analytics Studio',
        category: 'Navigation',
        icon: BarChart3,
        action: () => {
          onNavigate('workspace');
          onClose();
        },
        shortcut: 'W',
      },
      {
        id: 'nav-exp',
        title: 'Go to Export & Report Center',
        category: 'Navigation',
        icon: Download,
        action: () => {
          onNavigate('exports');
          onClose();
        },
        shortcut: 'E',
      },
      {
        id: 'act-run',
        title: 'Launch Autonomous Analysis Workflow',
        category: 'Quick Actions',
        icon: Play,
        action: () => {
          onTriggerQuickRun();
          onClose();
        },
        shortcut: 'R',
      },
    ];

    // Dataset search items
    const datasetCommands: CommandItem[] = datasets.map((ds) => ({
      id: `ds-${ds.id}`,
      title: `Dataset: ${ds.filename} (${(ds.rows || 0).toLocaleString()} rows, ${ds.columns || 0} cols)`,
      category: 'Datasets',
      icon: Database,
      action: () => {
        onSelectDataset(ds.id);
        onNavigate('datasets');
        onClose();
      },
    }));

    // Analysis search items
    const analysisCommands: CommandItem[] = analyses.map((anl) => ({
      id: `anl-${anl.id}`,
      title: `Analysis: Run #${anl.id.slice(0, 8)} (${anl.status.toUpperCase()})`,
      category: 'Analysis Runs',
      icon: FileCode,
      action: () => {
        onOpenAnalysis(anl.id);
        onNavigate('workspace');
        onClose();
      },
    }));

    return [...baseCommands, ...datasetCommands, ...analysisCommands];
  }, [datasets, analyses, onNavigate, onClose, onSelectDataset, onOpenAnalysis, onTriggerQuickRun]);

  const filteredCommands = useMemo(() => {
    if (!query.trim()) return commands;
    const q = query.toLowerCase();
    return commands.filter(
      (c) => c.title.toLowerCase().includes(q) || c.category.toLowerCase().includes(q)
    );
  }, [commands, query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div
        className="w-full max-w-xl glass-panel rounded-2xl border border-indigo-500/40 shadow-2xl overflow-hidden animate-scaleUp"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-800 bg-slate-900/90">
          <Search className="w-5 h-5 text-indigo-400 mr-3 shrink-0" />
          <input
            type="text"
            placeholder="Type a command, dataset name, or analysis run ID..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            autoFocus
            className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
          />
          <button
            onClick={onClose}
            className="p-1 text-slate-500 hover:text-slate-300 rounded-md hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Command List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredCommands.length === 0 ? (
            <div className="py-8 text-center text-slate-500 text-xs italic">
              No matching commands or resources found.
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;

              return (
                <div
                  key={cmd.id}
                  onClick={cmd.action}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-indigo-600/30 text-white border border-indigo-500/40 shadow-glow-indigo'
                      : 'text-slate-300 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`p-1.5 rounded-lg ${
                        isSelected ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-semibold truncate">{cmd.title}</div>
                      <div className="text-[10px] text-slate-500">{cmd.category}</div>
                    </div>
                  </div>

                  {cmd.shortcut && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                      {cmd.shortcut}
                    </span>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2 bg-slate-950/80 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center gap-2">
            <span>Navigation:</span>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono">
              ↑↓
            </kbd>
            <span>Select:</span>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono">
              Enter
            </kbd>
            <span>Close:</span>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono">
              Esc
            </kbd>
          </div>
          <div className="flex items-center gap-1 text-indigo-400 font-medium">
            <Sparkles className="w-3 h-3" /> AutoAnalyst AI
          </div>
        </div>
      </div>
    </div>
  );
};
