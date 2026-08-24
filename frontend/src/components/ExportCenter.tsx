import React, { useState } from 'react';
import { AnalysisRun } from '../types';
import {
  Download,
  FileText,
  Code,
  FileSpreadsheet,
  Eye,
  Layers,
  ExternalLink,
  Sparkles,
} from 'lucide-react';

interface ExportCenterProps {
  analysis: AnalysisRun | null;
}

export const ExportCenter: React.FC<ExportCenterProps> = ({ analysis }) => {
  const [activeView, setActiveView] = useState<'downloads' | 'preview'>('preview');

  if (!analysis) {
    return (
      <div className="glass-panel p-12 rounded-3xl text-center space-y-3 border border-slate-800 animate-fadeIn">
        <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto">
          <Download className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-white">No Analysis Artifacts Available</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Run or select an autonomous analysis to generate exportable executive reports, structured JSON telemetry, and model binaries.
        </p>
      </div>
    );
  }

  const handleDownload = (format: 'html' | 'json' | 'csv') => {
    window.open(`/api/v1/artifacts/${analysis.id}/download?format=${format}`, '_blank');
  };

  const reportUrl = `/api/v1/artifacts/${analysis.id}/download?format=html`;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-glow-indigo">
            <Download className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white">Enterprise Report & Export Studio</h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                Run #{analysis.id.slice(0, 8)}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Production analytical reports, interactive charts, and model-ready artifacts.
            </p>
          </div>
        </div>

        {/* View Mode & Actions */}
        <div className="flex items-center gap-3">
          <div className="flex items-center p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <button
              onClick={() => setActiveView('preview')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
                activeView === 'preview'
                  ? 'bg-indigo-600 text-white shadow-glow-indigo'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Live Report Preview</span>
            </button>

            <button
              onClick={() => setActiveView('downloads')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg font-semibold transition-all ${
                activeView === 'downloads'
                  ? 'bg-indigo-600 text-white shadow-glow-indigo'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Download Center</span>
            </button>
          </div>

          <button
            onClick={() => window.open(reportUrl, '_blank')}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 text-xs font-semibold transition-all"
            title="Open in new window"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Open in Tab</span>
          </button>
        </div>
      </div>

      {activeView === 'preview' ? (
        /* Live Embedded HTML Report Previewer */
        <div className="glass-panel p-4 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between px-2 py-1 text-xs">
            <div className="flex items-center gap-2 text-indigo-300 font-semibold">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Interactive Executive HTML Report • Print & PDF Ready</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleDownload('html')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-bold transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Save HTML</span>
              </button>
            </div>
          </div>

          <div className="w-full h-[780px] rounded-2xl overflow-hidden border border-slate-800/80 bg-slate-950 shadow-inner">
            <iframe
              src={reportUrl}
              title="AutoAnalyst Executive Report"
              className="w-full h-full border-0"
            />
          </div>
        </div>
      ) : (
        /* Export Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 1. Standalone HTML Executive Report */}
          <div className="glass-panel glass-card-hover p-6 rounded-3xl border border-indigo-500/30 flex flex-col justify-between space-y-5 relative overflow-hidden group">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-2xl bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 group-hover:scale-110 transition-transform">
                  <FileText className="w-6 h-6" />
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-300">
                  .HTML
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-white">Executive Strategy Report</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Self-contained, responsive HTML report featuring interactive visual charts, executive synthesis narrative, model benchmarks, and dimensional quality audit.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300 space-y-1">
                <div>Format: Standalone Interactive HTML</div>
                <div>Included: Plots, Tables, Findings</div>
              </div>
            </div>

            <button
              onClick={() => handleDownload('html')}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-glow-indigo transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Download HTML Report</span>
            </button>
          </div>

          {/* 2. Structured Machine-Readable JSON */}
          <div className="glass-panel glass-card-hover p-6 rounded-3xl border border-cyan-500/30 flex flex-col justify-between space-y-5 relative overflow-hidden group">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-2xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 group-hover:scale-110 transition-transform">
                  <Code className="w-6 h-6" />
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300">
                  .JSON
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-white">Analysis Telemetry & Metrics</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Raw structured JSON containing all multi-agent tool outputs, cross-validation leaderboard metrics, confusion matrices, correlation coefficients, and findings.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300 space-y-1">
                <div>Format: UTF-8 Structured JSON</div>
                <div>Schema: Complete Run Payload</div>
              </div>
            </div>

            <button
              onClick={() => handleDownload('json')}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-glow-cyan transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Download JSON Data</span>
            </button>
          </div>

          {/* 3. Preprocessed Cleaned Dataset CSV */}
          <div className="glass-panel glass-card-hover p-6 rounded-3xl border border-emerald-500/30 flex flex-col justify-between space-y-5 relative overflow-hidden group">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-2xl bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 group-hover:scale-110 transition-transform">
                  <FileSpreadsheet className="w-6 h-6" />
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300">
                  .CSV
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-white">Cleaned & Model-Ready CSV</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  Export the fully cleansed, imputed, deduplicated, and encoded dataset ready for enterprise production pipelines or external BI tools.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-[11px] font-mono text-slate-300 space-y-1">
                <div>Format: Delimited Comma CSV</div>
                <div>Preprocessing: Fully Cleaned</div>
              </div>
            </div>

            <button
              onClick={() => handleDownload('csv')}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-glow-emerald transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Download Cleaned CSV</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
