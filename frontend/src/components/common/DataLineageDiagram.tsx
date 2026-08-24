import React from 'react';
import {
  FileText,
  Search,
  Wrench,
  Binary,
  BrainCircuit,
  Activity,
  FileCheck,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';

interface DataLineageProps {
  currentStage?: string;
  datasetName?: string;
  championModel?: string;
}

export const DataLineageDiagram: React.FC<DataLineageProps> = ({
  datasetName = 'Dataset',
  championModel = 'Champion Model',
}) => {
  const stages = [
    {
      id: 'raw_ingestion',
      name: 'Raw Data Ingestion',
      icon: FileText,
      tag: datasetName,
      status: 'completed',
    },
    {
      id: 'profiling_agent',
      name: 'Schema Profiling',
      icon: Search,
      tag: 'Quality Audit',
      status: 'completed',
    },
    {
      id: 'preprocessing_agent',
      name: 'Adaptive Hygiene',
      icon: Wrench,
      tag: 'Imputation & Cleaning',
      status: 'completed',
    },
    {
      id: 'feature_encoding',
      name: 'Feature Vectors',
      icon: Binary,
      tag: 'One-Hot & Scaled',
      status: 'completed',
    },
    {
      id: 'ml_agent',
      name: 'Model Zoo Benchmark',
      icon: BrainCircuit,
      tag: championModel,
      status: 'completed',
    },
    {
      id: 'evaluation_agent',
      name: 'Diagnostic Testing',
      icon: Activity,
      tag: 'Holdout Validation',
      status: 'completed',
    },
    {
      id: 'reporting_agent',
      name: 'Strategic Synthesis',
      icon: FileCheck,
      tag: 'HTML & PDF Reports',
      status: 'completed',
    },
  ];

  return (
    <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Binary className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">End-to-End Analytical Data Lineage</h4>
            <p className="text-xs text-slate-400">Traceable transformation pipeline from raw bytes to predictive champion</p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" /> Pipeline Validated
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 pt-2">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isLast = idx === stages.length - 1;

          return (
            <div key={stage.id} className="relative flex flex-col justify-between p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 transition-all space-y-2 group">
              <div className="flex items-center justify-between">
                <div className="w-7 h-7 rounded-lg bg-indigo-500/15 text-indigo-300 flex items-center justify-center font-bold text-xs group-hover:scale-110 transition-transform">
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="text-[9px] font-mono text-slate-500">0{idx + 1}</span>
              </div>

              <div>
                <h5 className="text-xs font-bold text-white leading-tight">{stage.name}</h5>
                <p className="text-[10px] font-mono text-slate-400 mt-0.5 truncate">{stage.tag}</p>
              </div>

              <div className="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Verified
                </span>
                {!isLast && <ArrowRight className="w-3 h-3 text-slate-600 hidden lg:block" />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
