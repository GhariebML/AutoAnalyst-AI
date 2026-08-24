import React, { useState, useEffect } from 'react';
import { Navbar, NavTab } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { DatasetHub } from './components/DatasetHub';
import { AgentMonitor } from './components/AgentMonitor';
import { AnalyticsWorkspace } from './components/AnalyticsWorkspace';
import { ModelPlayground } from './components/ModelPlayground';
import { SystemHealthView } from './components/SystemHealthView';
import { ChatPanel } from './components/ChatPanel';
import { ExportCenter } from './components/ExportCenter';
import { HITLApprovalModal } from './components/HITLApprovalModal';
import { CommandPalette } from './components/CommandPalette';
import {
  fetchDatasets,
  fetchAllAnalyses,
  fetchAnalysis,
  createAnalysis,
  approveHITLPlan,
  subscribeToRunEvents,
} from './api/client';
import { Dataset, AnalysisRun, AgentTelemetry } from './types';
import { X, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('dashboard');
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [analyses, setAnalyses] = useState<AnalysisRun[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisRun | null>(null);

  // Real-time run tracking state
  const [isRunning, setIsRunning] = useState(false);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<string>('idle');
  const [events, setEvents] = useState<Array<{ type: string; message: string; timestamp: string; data?: any }>>([]);
  const [agentTelemetry, setAgentTelemetry] = useState<Record<string, AgentTelemetry>>({});

  // HITL state
  const [isHITLModalOpen, setIsHITLModalOpen] = useState(false);
  const [hitlPrompt, setHitlPrompt] = useState<string | null>(null);

  // Command Palette & Chat Overlay
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Global Ctrl+K / Cmd+K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Initial Data Fetch
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [dsData, anlData] = await Promise.all([fetchDatasets(), fetchAllAnalyses()]);
        setDatasets(dsData);
        setAnalyses(anlData);
        if (anlData.length > 0) {
          setCurrentAnalysis(anlData[0]);
        }
      } catch (err) {
        console.error('Failed to load initial workspace data:', err);
      }
    };
    loadInitialData();
  }, []);

  // Poll analysis details until completed
  useEffect(() => {
    if (!isRunning || !activeRunId) return;

    const interval = setInterval(async () => {
      try {
        const updated = await fetchAnalysis(activeRunId);
        if (updated) {
          setCurrentAnalysis(updated);
          if (updated.status === 'completed' || updated.status === 'failed') {
            setIsRunning(false);
            setRunStatus(updated.status);
            // Refresh history
            const freshHistory = await fetchAllAnalyses();
            setAnalyses(freshHistory);
            clearInterval(interval);
          }
        }
      } catch (err) {
        console.error('Error polling analysis state:', err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isRunning, activeRunId]);

  // Subscribe to SSE events
  useEffect(() => {
    if (!activeRunId) return;

    const unsubscribe = subscribeToRunEvents(
      activeRunId,
      (event) => {
        setEvents((prev) => [
          {
            type: event.type,
            message: event.message || `Event: ${event.type}`,
            timestamp: event.timestamp || new Date().toISOString(),
            data: event.data,
          },
          ...prev,
        ]);

        if (event.type === 'AGENT_STARTED' && event.agent_name) {
          setCurrentAgent(event.agent_name);
          setAgentTelemetry((prev) => ({
            ...prev,
            [event.agent_name]: {
              agent_name: event.agent_name,
              status: 'active',
              duration_ms: 0,
            },
          }));
        } else if (event.type === 'AGENT_COMPLETED' && event.agent_name) {
          setAgentTelemetry((prev) => ({
            ...prev,
            [event.agent_name]: {
              agent_name: event.agent_name,
              status: 'completed',
              duration_ms: event.data?.duration_ms || 0,
              actions_taken: event.data?.actions_taken || [],
              findings: event.data?.findings || [],
              recommendations: event.data?.recommendations || [],
            },
          }));
        } else if (event.type === 'HITL_PAUSED') {
          setIsHITLModalOpen(true);
          setHitlPrompt(event.data?.prompt || 'Human approval required to proceed with data transformations.');
          setRunStatus('paused_hitl');
        } else if (event.type === 'RUN_COMPLETED') {
          setIsRunning(false);
          setRunStatus('completed');
          fetchAnalysis(activeRunId).then((fullRun) => {
            if (fullRun) setCurrentAnalysis(fullRun);
          });
        }
      },
      (err) => console.error('SSE Error:', err)
    );

    return () => unsubscribe();
  }, [activeRunId]);

  const handleStartAnalysis = async (datasetId: string, targetCol?: string) => {
    try {
      setIsRunning(true);
      setRunStatus('running');
      setEvents([]);
      setAgentTelemetry({});

      const newRun = await createAnalysis(datasetId, targetCol);
      setActiveRunId(newRun.id);
      setCurrentAnalysis(newRun);
      setActiveTab('workspace');

      // Refresh list
      const freshHistory = await fetchAllAnalyses();
      setAnalyses(freshHistory);
    } catch (err: any) {
      console.error('Failed to trigger analysis run:', err);
      setIsRunning(false);
      setRunStatus('failed');
      alert(`Execution Failed: ${err.message}`);
    }
  };

  const handleHITLApprove = async (approved: boolean, modifications?: Record<string, any>) => {
    if (!activeRunId) return;
    try {
      if (approved) {
        await approveHITLPlan(activeRunId, modifications);
        setIsHITLModalOpen(false);
        setRunStatus('running');
      } else {
        setIsHITLModalOpen(false);
        setIsRunning(false);
        setRunStatus('failed');
      }
    } catch (err) {
      console.error('HITL approval error:', err);
    }
  };

  const handleOpenAnalysisById = async (id: string) => {
    try {
      const found = analyses.find((a) => a.id === id) || (await fetchAnalysis(id));
      if (found) {
        setCurrentAnalysis(found);
        setActiveRunId(found.id);
        setActiveTab('analytics');
      }
    } catch (err) {
      console.error('Failed to open analysis by id:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isRunning={isRunning}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        activeDatasetName={currentAnalysis?.dataset_id}
        activeRunId={currentAnalysis?.id}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard
            analyses={analyses}
            datasets={datasets}
            onSelectDataset={(_id) => setActiveTab('datasets')}
            onOpenAnalysis={handleOpenAnalysisById}
            onNewAnalysis={() => setActiveTab('datasets')}
          />
        )}

        {activeTab === 'datasets' && (
          <DatasetHub
            datasets={datasets}
            onDatasetUploaded={(newDs) => setDatasets((prev) => [newDs, ...prev])}
            onLaunchAnalysis={handleStartAnalysis}
          />
        )}

        {activeTab === 'workspace' && (
          <div className="space-y-6 animate-fadeIn">
            <AgentMonitor
              currentAgent={currentAgent}
              agentTelemetry={agentTelemetry}
              events={events}
              isRunning={isRunning}
              status={runStatus}
              analysis={currentAnalysis}
              onRequestApproval={() => setIsHITLModalOpen(true)}
            />
          </div>
        )}

        {activeTab === 'analytics' && (
          <AnalyticsWorkspace analysis={currentAnalysis} />
        )}

        {activeTab === 'playground' && (
          <ModelPlayground
            currentAnalysis={currentAnalysis}
            analyses={analyses}
            onSelectAnalysis={(a) => {
              setCurrentAnalysis(a);
              setActiveRunId(a.id);
            }}
          />
        )}

        {activeTab === 'exports' && <ExportCenter analysis={currentAnalysis} />}

        {activeTab === 'health' && <SystemHealthView />}
      </main>

      {/* HITL Governance Approval Modal */}
      {activeRunId && (
        <HITLApprovalModal
          isOpen={isHITLModalOpen}
          onClose={() => setIsHITLModalOpen(false)}
          runId={activeRunId}
          humanPrompt={hitlPrompt}
          onApprove={handleHITLApprove}
        />
      )}

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onNavigate={(tab) => setActiveTab(tab as NavTab)}
        datasets={datasets}
        analyses={analyses}
        onSelectDataset={(_id) => setActiveTab('datasets')}
        onOpenAnalysis={handleOpenAnalysisById}
        onTriggerQuickRun={() => setActiveTab('datasets')}
      />

      {/* Floating AI Analyst Copilot Button & Drawer */}
      <div className="fixed bottom-6 right-6 z-40">
        {isChatOpen ? (
          <div className="w-96 shadow-2xl relative">
            <button
              onClick={() => setIsChatOpen(false)}
              className="absolute top-3.5 right-3.5 z-10 p-1 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
            <ChatPanel analysisId={currentAnalysis?.id || activeRunId} />
          </div>
        ) : (
          <button
            onClick={() => setIsChatOpen(true)}
            className="flex items-center gap-2 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 to-cyan-500 text-white font-bold text-xs shadow-glow-indigo hover:scale-105 transition-all group"
          >
            <Sparkles className="w-4 h-4 group-hover:rotate-12 transition-transform" />
            <span>AI Analyst Copilot</span>
          </button>
        )}
      </div>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-slate-950/80 py-6 text-center text-xs text-slate-500 font-mono">
        AutoAnalyst AI • Autonomous Multi-Agent Data Intelligence & Machine Learning Platform
      </footer>
    </div>
  );
};

export default App;
