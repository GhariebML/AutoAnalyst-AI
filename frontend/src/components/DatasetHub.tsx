import React, { useState } from 'react';
import { Dataset, DatasetPreview } from '../types';
import { uploadDatasetFile, fetchDatasetPreview } from '../api/client';
import {
  UploadCloud,
  FileSpreadsheet,
  AlertCircle,
  Database,
  Search,
  Sparkles,
  Zap,
} from 'lucide-react';

interface DatasetHubProps {
  datasets: Dataset[];
  onDatasetUploaded: (dataset: Dataset) => void;
  onLaunchAnalysis: (datasetId: string, targetCol?: string) => void;
}

export const DatasetHub: React.FC<DatasetHubProps> = ({
  datasets,
  onDatasetUploaded,
  onLaunchAnalysis,
}) => {
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(
    datasets[0]?.id || null
  );
  const [preview, setPreview] = useState<DatasetPreview | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [targetColumn, setTargetColumn] = useState<string>('');
  const [searchFilter, setSearchFilter] = useState<string>('');

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId) || datasets[0];

  const columnList =
    preview?.column_names ||
    (preview?.data_preview && preview.data_preview.length > 0
      ? Object.keys(preview.data_preview[0])
      : []);

  // Load preview when selecting dataset
  const handleSelectDataset = async (datasetId: string) => {
    setSelectedDatasetId(datasetId);
    setIsLoadingPreview(true);
    try {
      const data = await fetchDatasetPreview(datasetId);
      setPreview(data);
      const cols = data.column_names || (data.data_preview && data.data_preview.length > 0 ? Object.keys(data.data_preview[0]) : []);
      if (cols.length > 0) {
        const candidate =
          cols.find((c: string) =>
            ['target', 'label', 'class', 'price', 'salary', 'churn', 'income'].includes(c.toLowerCase())
          ) || cols[cols.length - 1];
        setTargetColumn(candidate);
      }
    } catch {
      // preview error handled gracefully
    } finally {
      setIsLoadingPreview(false);
    }
  };

  // Upload handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const newDataset = await uploadDatasetFile(file);
      onDatasetUploaded(newDataset);
      handleSelectDataset(newDataset.id);
    } catch (err: any) {
      setUploadError(err?.message || 'Failed to upload and profile dataset.');
    } finally {
      setIsUploading(false);
    }
  };

  // Filter preview rows
  const filteredRows = (preview?.data_preview || []).filter((row) => {
    if (!searchFilter.trim()) return true;
    return Object.values(row).some((val) =>
      String(val).toLowerCase().includes(searchFilter.toLowerCase())
    );
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Upload Zone & Hub Header */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Drag & Drop Upload Card */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <UploadCloud className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white">Ingest & Profile Dataset</h3>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">CSV</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">XLSX</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">PARQUET</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">JSON</span>
            </div>
          </div>

          <label className="relative flex flex-col items-center justify-center p-8 border-2 border-dashed border-slate-700 hover:border-cyan-400/60 rounded-2xl cursor-pointer bg-slate-900/40 hover:bg-slate-850/70 transition-all group overflow-hidden">
            <input
              type="file"
              accept=".csv,.xlsx,.xls,.parquet,.json,.db,.sqlite"
              onChange={handleFileUpload}
              disabled={isUploading}
              className="hidden"
            />
            <div className="p-4 rounded-2xl bg-cyan-500/10 text-cyan-400 group-hover:scale-110 transition-transform mb-3">
              <UploadCloud className="w-8 h-8" />
            </div>
            <p className="text-sm font-bold text-white text-center">
              {isUploading ? 'Ingesting & profiling schema...' : 'Drop your dataset here or click to browse'}
            </p>
            <p className="text-xs text-slate-400 text-center mt-1">
              Supports CSV, Excel, Parquet, JSON, and SQLite with automated schema health scoring
            </p>

            {isUploading && (
              <div className="w-48 h-1.5 rounded-full bg-slate-800 overflow-hidden mt-4">
                <div className="h-full bg-gradient-to-r from-cyan-400 to-indigo-500 animate-shimmer"></div>
              </div>
            )}
          </label>

          {uploadError && (
            <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Dataset Quick Launch Card */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <Sparkles className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white">Analysis Launchpad</h3>
            </div>

            {selectedDataset ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                  <div className="text-slate-400">Selected Dataset:</div>
                  <div className="font-bold text-white text-sm truncate">{selectedDataset.filename}</div>
                  <div className="text-slate-400 font-mono">
                    {(selectedDataset.rows || 0).toLocaleString()} rows • {selectedDataset.columns || 0} columns
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400 font-semibold">Target Column (Optional):</label>
                  <select
                    value={targetColumn}
                    onChange={(e) => setTargetColumn(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono text-xs focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Auto-Detect / Unsupervised Mode</option>
                    {columnList.map((col: string) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              <div className="py-6 text-center text-slate-500 text-xs italic">
                Upload or select a dataset to configure the autonomous run.
              </div>
            )}
          </div>

          <button
            onClick={() => selectedDataset && onLaunchAnalysis(selectedDataset.id, targetColumn)}
            disabled={!selectedDataset || isUploading}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-500 text-white font-bold text-sm shadow-glow-indigo hover:opacity-95 disabled:opacity-50 transition-all"
          >
            <Zap className="w-4 h-4" />
            <span>Launch Multi-Agent Run</span>
          </button>
        </div>
      </div>

      {/* Dataset Selection Chips & Preview Table */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-6">
        {/* Selector Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Interactive Data Explorer</h3>
              <p className="text-xs text-slate-400">Inspect schema dtypes, health score, and preview sample rows</p>
            </div>
          </div>

          {/* Search bar inside table */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search values in preview..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
            />
          </div>
        </div>

        {/* Dataset Selection Tabs */}
        {datasets.length > 0 && (
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {datasets.map((ds) => (
              <button
                key={ds.id}
                onClick={() => handleSelectDataset(ds.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold shrink-0 transition-all ${
                  selectedDatasetId === ds.id
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan'
                    : 'bg-slate-900/60 text-slate-400 border border-slate-800 hover:bg-slate-800/60'
                }`}
              >
                <FileSpreadsheet className="w-3.5 h-3.5" />
                <span className="truncate max-w-[140px]">{ds.filename}</span>
                <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                  {ds.health_score?.toFixed(0) || 100}%
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Data Table Preview */}
        {isLoadingPreview ? (
          <div className="py-16 text-center text-slate-400 text-xs font-mono">
            Loading preview records and schema metrics...
          </div>
        ) : preview && columnList.length > 0 ? (
          <div className="space-y-4">
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-950/60">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-300 font-mono">
                    <th className="py-3 px-4 text-slate-500 text-[10px] w-12">#</th>
                    {columnList.map((col: string) => {
                      const dtype = preview.dtypes?.[col] || 'unknown';
                      const isNumeric = ['int64', 'float64', 'int32', 'float32', 'number'].some((t) =>
                        dtype.toLowerCase().includes(t)
                      );

                      return (
                        <th key={col} className="py-3 px-4 font-semibold whitespace-nowrap">
                          <div className="flex items-center gap-1.5">
                            <span>{col}</span>
                            <span
                              className={`px-1.5 py-0.2 text-[9px] rounded font-mono ${
                                isNumeric
                                  ? 'bg-indigo-500/20 text-indigo-300'
                                  : 'bg-purple-500/20 text-purple-300'
                              }`}
                            >
                              {dtype}
                            </span>
                          </div>
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {filteredRows.slice(0, 10).map((row, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-900/60 transition-colors font-mono text-[11px]">
                      <td className="py-2.5 px-4 text-slate-500 text-[10px]">{rIdx + 1}</td>
                      {columnList.map((col: string) => (
                        <td key={col} className="py-2.5 px-4 text-slate-300 whitespace-nowrap">
                          {row[col] === null || row[col] === undefined ? (
                            <span className="text-rose-400 italic">null</span>
                          ) : (
                            String(row[col])
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 px-2 font-mono">
              <span>Showing sample records ({filteredRows.length} rows previewed)</span>
              <span className="text-cyan-300">
                Composite Quality Score: {preview.health_score?.toFixed(1) || 100}%
              </span>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-slate-500 text-xs italic">
            Select a dataset above to inspect its schema and data preview.
          </div>
        )}
      </div>
    </div>
  );
};
