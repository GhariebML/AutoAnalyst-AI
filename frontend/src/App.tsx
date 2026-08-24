import React, { useState, useEffect } from 'react';
import { Navbar, NavTab } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { DatasetHub } from './components/DatasetHub';
import { AgentMonitor } from './components/AgentMonitor';
import { AnalyticsWorkspace } from './components/AnalyticsWorkspace';
import { SystemHealthView } from './components/SystemHealthView';
import { ChatPanel } from './components/ChatPanel';
import { ExportCenter } from './components/ExportCenter';
import { HITLApprovalModal } from './components/HITLApprovalModal';
import { CommandPalette } from './components/CommandPalette';
import {
  fetchDatasets,
  fetchAnalyses,
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
        const [dsData, anlData] = await Promise.all([fetchDatasets(), fetchAnalyses()]);
        setDatasets(dsData);
        setAnalyses(anlData);
        if (anlData.length > 0) {
          const latest = await fetchAnalysis(anlData[0].id);
          setCurrentAnalysis(latest);
        }
      } catch (err) {
        console.error('Failed to load initial data:', err);
      }
    };
    loadInitialData();
  }, []);

  // Launch Analysis
  const handleLaunchAnalysis = async (datasetId: string, targetCol?: string) => {
    try {
      setIsRunning(true);
      setRunStatus('running');
      setEvents([]);
      setAgentTelemetry({});
      setActiveTab('workspace');

      const run = await createAnalysis(datasetId, targetCol || undefined, 'full');
      setActiveRunId(run.id);

      // Subscribe to live SSE events
      subscribeToRunEvents(
        run.id,
        (event) => {
          setEvents((prev) => [...prev, event]);

          if (event.type === 'AGENT_STARTED') {
            setCurrentAgent(event.agent_name || null);
          } else if (event.type === 'AGENT_COMPLETED' && event.agent_name) {
            setAgentTelemetry((prev) => ({
              ...prev,
              [event.agent_name]: {
                agent_name: event.agent_name,
                status: 'completed',
                duration_ms: event.data?.duration_ms || 1000,
                actions_taken: event.data?.actions_taken || [],
                findings: event.data?.findings || [],
                recommendations: event.data?.recommendations || [],
              },
            }));
          } else if (event.type === 'HITL_PAUSED') {
            setRunStatus('paused_hitl');
            setHitlPrompt(event.data?.human_prompt || null);
            setIsHITLModalOpen(true);
          } else if (event.type === 'RUN_COMPLETED') {
            setIsRunning(false);
            setRunStatus('completed');
            setCurrentAgent(null);
            // Refresh analysis run and history
            fetchAnalysis(run.id).then((full) => {
              setCurrentAnalysis(full);
              fetchAnalyses().then(setAnalyses);
            });
          } else if (event.type === 'RUN_FAILED') {
            setIsRunning(false);
            setRunStatus('failed');
            setCurrentAgent(null);
          }
        },
        (error) => {
          console.error('SSE Error:', error);
          setIsRunning(false);
        }
      );
    } catch (err) {
      console.error('Launch Error:', err);
      setIsRunning(false);
    }
  };

  // HITL Approval submission
  const handleHITLApprove = async (approved: boolean, modifications?: Record<string, any>) => {
    if (!activeRunId) return;
    try {
      await approveHITLPlan(activeRunId, approved, modifications);
      setRunStatus('running');
      setIsHITLModalOpen(false);
    } catch (err) {
      console.error('Approval Error:', err);
    }
  };

  const handleOpenAnalysis = async (anlId: string) => {
    try {
      const full = await fetchAnalysis(anlId);
      setCurrentAnalysis(full);
      setActiveTab('analytics');
    } catch (err) {
      console.error('Failed to open analysis:', err);
    }
  };

  return (
    <div className="min-h-screen bg-background-darkest text-slate-100 flex flex-col bg-grid-pattern bg-radial-gradient">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        isRunning={isRunning}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        activeDatasetName={datasets.find((d) => d.id === currentAnalysis?.dataset_id)?.filename}
        activeRunId={currentAnalysis?.id}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard
            datasets={datasets}
            analyses={analyses}
            onSelectDataset={() => setActiveTab('datasets')}
            onOpenAnalysis={handleOpenAnalysis}
            onNewAnalysis={() => setActiveTab('datasets')}
          />
        )}

        {activeTab === 'datasets' && (
          <DatasetHub
            datasets={datasets}
            onDatasetUploaded={(newDs) => setDatasets((prev) => [newDs, ...prev])}
            onLaunchAnalysis={handleLaunchAnalysis}
          />
        )}

        {activeTab === 'workspace' && (
          <div className="space-y-8">
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
        onSelectDataset={() => setActiveTab('datasets')}
        onOpenAnalysis={handleOpenAnalysis}
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
