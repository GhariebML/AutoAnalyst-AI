import React, { useState, useEffect } from 'react';
import { AnalysisRun, ModelSchemaResponse, PredictionResult } from '../types';
import { fetchModelSchema, predictModelRecord } from '../api/client';
import {
  Sliders,
  Sparkles,
  Gauge,
  Layers,
  RefreshCw,
  Zap,
  BarChart3,
  TrendingUp,
} from 'lucide-react';

interface ModelPlaygroundProps {
  currentAnalysis: AnalysisRun | null;
  analyses: AnalysisRun[];
  onSelectAnalysis: (analysis: AnalysisRun) => void;
}

export const ModelPlayground: React.FC<ModelPlaygroundProps> = ({
  currentAnalysis,
  analyses,
  onSelectAnalysis,
}) => {
  const [schema, setSchema] = useState<ModelSchemaResponse | null>(null);
  const [featureValues, setFeatureValues] = useState<Record<string, any>>({});
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Filter analyses that completed and have a target column
  const eligibleAnalyses = analyses.filter(
    (a) => a.status === 'completed' && a.target_column
  );

  useEffect(() => {
    if (!currentAnalysis || !currentAnalysis.id) return;
    loadSchema(currentAnalysis.id);
  }, [currentAnalysis?.id]);

  const loadSchema = async (analysisId: string) => {
    setLoadingSchema(true);
    setErrorMsg(null);
    try {
      const res = await fetchModelSchema(analysisId);
      setSchema(res);
      // Initialize feature values with defaults
      const initialVals: Record<string, any> = {};
      res.features.forEach((f) => {
        initialVals[f.name] = f.default_value ?? (f.min_value || 0);
      });
      setFeatureValues(initialVals);
      // Run initial prediction
      runPrediction(analysisId, initialVals);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load model schema');
    } finally {
      setLoadingSchema(false);
    }
  };

  const handleSliderChange = (featName: string, val: number) => {
    const nextVals = { ...featureValues, [featName]: val };
    setFeatureValues(nextVals);
    if (currentAnalysis?.id) {
      runPrediction(currentAnalysis.id, nextVals);
    }
  };

  const handleSelectChange = (featName: string, val: string) => {
    const nextVals = { ...featureValues, [featName]: val };
    setFeatureValues(nextVals);
    if (currentAnalysis?.id) {
      runPrediction(currentAnalysis.id, nextVals);
    }
  };

  const runPrediction = async (analysisId: string, vals: Record<string, any>) => {
    setPredicting(true);
    try {
      const res = await predictModelRecord(analysisId, vals);
      setPrediction(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Inference failed');
    } finally {
      setPredicting(false);
    }
  };

  const resetToDefaults = () => {
    if (!schema) return;
    const initialVals: Record<string, any> = {};
    schema.features.forEach((f) => {
      initialVals[f.name] = f.default_value ?? (f.min_value || 0);
    });
    setFeatureValues(initialVals);
    if (currentAnalysis?.id) {
      runPrediction(currentAnalysis.id, initialVals);
    }
  };

  if (eligibleAnalyses.length === 0 && !currentAnalysis?.target_column) {
    return (
      <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center space-y-4 max-w-2xl mx-auto my-12 animate-fadeIn">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400">
          <Sliders className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-white">No Model Servings Available</h3>
        <p className="text-sm text-slate-400">
          Execute an autonomous multi-agent analysis on any dataset with a configured target column to activate real-time model serving and the interactive What-If Simulator.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header & Model Selector */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-400 text-white shadow-glow-indigo">
              <Zap className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Real-Time Model Serving & What-If Simulator
            </h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Live Inference
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Adjust dynamic feature inputs in real time to simulate model predictions and evaluate what-if business scenarios.
          </p>
        </div>

        {/* Model Selector dropdown */}
        <div className="flex items-center gap-3">
          <div className="text-xs text-slate-400">Serving Run:</div>
          <select
            value={currentAnalysis?.id || ''}
            onChange={(e) => {
              const selected = analyses.find((a) => a.id === e.target.value);
              if (selected) onSelectAnalysis(selected);
            }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            {eligibleAnalyses.map((a) => (
              <option key={a.id} value={a.id}>
                #{a.id.slice(0, 8)} • {a.champion_model_name || 'Model'} ({a.target_column})
              </option>
            ))}
          </select>
          <button
            onClick={resetToDefaults}
            className="p-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-300 hover:text-white transition-all"
            title="Reset feature values to baseline means"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {loadingSchema ? (
        <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center text-slate-400 text-sm italic">
          Loading model feature schema and deploying inference runtime...
        </div>
      ) : errorMsg ? (
        <div className="glass-panel p-6 rounded-3xl border border-rose-500/30 bg-rose-500/5 text-rose-300 text-xs">
          {errorMsg}
        </div>
      ) : schema ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Dynamic Feature Controls */}
          <div className="lg:col-span-7 space-y-4">
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white">Dynamic Feature Inputs</h3>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {schema.features.length} features configured
                </span>
              </div>

              <div className="space-y-4 max-h-[580px] overflow-y-auto pr-2">
                {schema.features.map((feat) => {
                  const val = featureValues[feat.name];
                  if (feat.is_numeric) {
                    const min = feat.min_value ?? 0;
                    const max = feat.max_value ?? 100;
                    const step = max - min > 50 ? 1 : 0.1;

                    return (
                      <div
                        key={feat.name}
                        className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2 hover:border-slate-700 transition-all"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-mono text-slate-200 font-semibold">{feat.name}</span>
                          <span className="font-mono font-bold text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                            {typeof val === 'number' ? val.toFixed(step < 1 ? 2 : 0) : val}
                          </span>
                        </div>
                        <input
                          type="range"
                          min={min}
                          max={max}
                          step={step}
                          value={typeof val === 'number' ? val : min}
                          onChange={(e) => handleSliderChange(feat.name, parseFloat(e.target.value))}
                          className="w-full accent-indigo-500 cursor-pointer h-1.5 bg-slate-700 rounded-lg"
                        />
                        <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                          <span>Min: {min.toFixed(1)}</span>
                          <span>Default: {feat.default_value?.toFixed(1) || '0'}</span>
                          <span>Max: {max.toFixed(1)}</span>
                        </div>
                      </div>
                    );
                  } else {
                    return (
                      <div
                        key={feat.name}
                        className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2 hover:border-slate-700 transition-all"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-mono text-slate-200 font-semibold">{feat.name}</span>
                          <span className="text-[10px] text-slate-400 uppercase font-mono">{feat.dtype}</span>
                        </div>
                        <select
                          value={val || ''}
                          onChange={(e) => handleSelectChange(feat.name, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
                        >
                          {feat.categories && feat.categories.length > 0 ? (
                            feat.categories.map((cat) => (
                              <option key={cat} value={cat}>
                                {cat}
                              </option>
                            ))
                          ) : (
                            <option value={val || 'value'}>{val || 'Default Value'}</option>
                          )}
                        </select>
                      </div>
                    );
                  }
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Live Model Output & Explainability */}
          <div className="lg:col-span-5 space-y-6">
            {/* Live Prediction Display */}
            <div className="glass-panel p-6 rounded-3xl border border-indigo-500/30 bg-gradient-to-b from-indigo-950/20 to-slate-950/80 space-y-5 shadow-glow-indigo">
              <div className="flex items-center justify-between pb-3 border-b border-indigo-500/20">
                <div className="flex items-center gap-2">
                  <Gauge className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Live Prediction Output</h3>
                </div>
                {predicting && <Sparkles className="w-4 h-4 text-cyan-400 animate-spin" />}
              </div>

              {prediction ? (
                <div className="space-y-5">
                  <div className="text-center py-4 bg-slate-900/80 rounded-2xl border border-slate-800 space-y-1">
                    <div className="text-xs text-slate-400 font-medium">Target: {schema.target_column}</div>
                    <div className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-indigo-200 to-purple-300 tracking-tight font-mono">
                      {prediction.prediction_label}
                    </div>
                    <div className="flex items-center justify-center gap-2 pt-2">
                      <span className="text-[11px] text-slate-400">Inference Confidence:</span>
                      <span className="text-xs font-mono font-bold text-emerald-400">
                        {(prediction.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* Class Probabilities if available */}
                  {prediction.probabilities && (
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                        <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Class Probabilities</span>
                      </div>
                      <div className="space-y-1.5">
                        {Object.entries(prediction.probabilities).map(([cls, prob]) => (
                          <div key={cls} className="space-y-1">
                            <div className="flex items-center justify-between text-[11px] font-mono">
                              <span className="text-slate-300">{cls}</span>
                              <span className="text-cyan-300 font-bold">{(prob * 100).toFixed(1)}%</span>
                            </div>
                            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full transition-all duration-300"
                                style={{ width: `${Math.min(prob * 100, 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Top Contributing Feature Influences */}
                  {prediction.feature_contributions && prediction.feature_contributions.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-800">
                      <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                        <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Top Feature Influences</span>
                      </div>
                      <div className="space-y-1.5">
                        {prediction.feature_contributions.map((fc, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between text-xs p-2 rounded-xl bg-slate-900/50 border border-slate-800"
                          >
                            <span className="font-mono text-slate-300">{fc.feature}</span>
                            <span className="font-mono font-bold text-cyan-300">
                              {(fc.weight * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400 text-xs italic">
                  Move any feature slider to calculate prediction...
                </div>
              )}
            </div>

            {/* Model Metadata Card */}
            <div className="glass-panel p-5 rounded-3xl border border-slate-800 space-y-3">
              <div className="flex items-center gap-2 text-xs font-bold text-white">
                <Layers className="w-4 h-4 text-purple-400" />
                <span>Active Champion Model Specifications</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Architecture</div>
                  <div className="text-slate-200 font-bold truncate">{schema.model_name}</div>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-[10px] text-slate-400">Task Mode</div>
                  <div className="text-cyan-300 font-bold uppercase">{schema.task_type}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
