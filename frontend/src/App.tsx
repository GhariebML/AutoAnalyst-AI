import './App.css'
import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { CampaignBriefForm } from './components/CampaignBriefForm'
import { LiveOrchestration } from './components/LiveOrchestration'
import { ResultDisplay } from './components/ResultDisplay'
import { StrategyView, ResearchView, SavedView, SettingsView, DashboardView, AnalyticsView } from './components/SidebarViews'
import { useTaskPolling } from './hooks/useTaskPolling'
import { campaignService } from './services/api'
import { useAppStore } from './store/useAppStore'
import type { ContentOutput } from './types'
import {
  Target,
  Search,
  FileText,
  Settings as SettingsIcon,
  Bell,
  User,
  Zap,
  CheckCircle2,
  Edit3,
  Rocket,
  Plus,
  LayoutDashboard
} from 'lucide-react'

function App() {
  const navigate = useNavigate()
  const location = useLocation()
  
  // Zustand Global State
  const { 
    activeAgent, setActiveAgent, 
    currentTaskId, setCurrentTaskId, 
    theme, toggleTheme 
  } = useAppStore()

  // Local State for specific view elements
  const [campaignId, setCampaignId] = useState<string | null>(null)
  const [results, setResults] = useState<ContentOutput | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)

  // Derive active tab from URL path
  const currentPath = location.pathname;
  const activeTopTab = currentPath.includes('/dashboard') ? 'Dashboard' 
                     : currentPath.includes('/analytics') ? 'Analytics' 
                     : 'Campaigns'

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  // React Query Task Polling
  const { status, loading, error } = useTaskPolling(currentTaskId)

  const handleBriefSubmit = (taskId: string) => {
    setCurrentTaskId(taskId)
    setCampaignId(taskId)
    setResults(null)
  }

  const handleNewCampaign = () => {
    setCurrentTaskId(null)
    setCampaignId(null)
    setResults(null)
    setActiveAgent('content')
    navigate('/campaigns')
  }

  const handleTaskComplete = async () => {
    if (campaignId && status?.status === 'completed' && !results) {
      try {
        const content = await campaignService.getCampaignContent(campaignId)
        setResults(content)
      } catch (err) {
        console.error('Failed to fetch results:', err)
      }
    }
  }

  useEffect(() => {
    if (status?.status === 'completed' && !results) {
      handleTaskComplete()
    }
  }, [status, results])

  const handleDownloadAssets = async () => {
    if (!campaignId) return
    setIsDownloading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      const blob = await campaignService.downloadDesignAssets(campaignId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `campaign-${campaignId}-assets.zip`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Failed to download assets:', err)
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="flex h-screen bg-[var(--bg-main)] overflow-hidden text-[var(--text-main)] transition-colors duration-500 relative">
      {/* Background Animated Blobs for Premium Depth */}
      <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-primary/20 rounded-full mix-blend-multiply filter blur-[100px] opacity-50 animate-blob pointer-events-none dark:mix-blend-screen" />
      <div className="absolute top-[20%] right-[-10%] w-[35vw] h-[35vw] bg-purple-500/20 rounded-full mix-blend-multiply filter blur-[100px] opacity-40 animate-blob animation-delay-2000 pointer-events-none dark:mix-blend-screen" />
      <div className="absolute bottom-[-20%] left-[20%] w-[45vw] h-[45vw] bg-accent/20 rounded-full mix-blend-multiply filter blur-[120px] opacity-30 animate-blob animation-delay-4000 pointer-events-none dark:mix-blend-screen" />

      {/* ── Sidebar ── */}
      <aside className="w-[240px] glass-panel border-r border-[var(--border-main)] flex flex-col z-30 shrink-0 transition-colors duration-300">
        <div className="p-6 flex items-center gap-3 border-b border-[var(--border-main)]">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-purple-500 rounded-xl flex items-center justify-center shadow-glow">
            <Zap className="text-white w-5 h-5" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight block leading-none text-slate-900 dark:text-white">AdPilot</span>
            <span className="text-[10px] text-primary font-mono uppercase tracking-widest font-semibold mt-1 block">v3.0 Enterprise</span>
          </div>
        </div>

        <nav className="flex-1 px-3 py-5 space-y-1">
          {[
            { id: 'strategy', label: 'Strategy Insights', icon: Target },
            { id: 'research', label: 'Audience Research', icon: Search },
            { id: 'content', label: 'Content Agent', icon: FileText, badge: true },
            { id: 'saved', label: 'Saved Content', icon: LayoutDashboard },
            { id: 'settings', label: 'Settings', icon: SettingsIcon },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveAgent(item.id as typeof activeAgent)
                navigate('/campaigns')
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  activeAgent === item.id && activeTopTab === 'Campaigns'
                    ? 'bg-primary/10 text-primary'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-slate-700 dark:hover:text-slate-200'
                }`}
            >
              <item.icon size={17} />
              <span className="truncate">{item.label}</span>
                {item.badge && activeAgent === item.id && activeTopTab === 'Campaigns' && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary animate-pulse shrink-0" />
              )}
            </button>
          ))}
        </nav>

        <div className="p-3 border-t border-white/5 space-y-3">
          <button
            onClick={handleNewCampaign}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-bold text-primary border border-primary/20 bg-primary/5 hover:bg-primary/10 transition-all"
          >
            <Plus size={15} />
            New Campaign
          </button>
          <div className="flex items-center gap-2 px-1">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-teal-500 flex items-center justify-center shrink-0">
              <User size={14} className="text-white" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-bold truncate leading-tight text-slate-900">Admin</p>
              <p className="text-[9px] text-slate-500 font-mono uppercase tracking-widest">Enterprise</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">

        {/* Top Bar */}
        <header className="h-16 glass-panel border-b border-[var(--border-main)] px-8 flex items-center justify-between z-20 shrink-0 transition-colors duration-300">
          <div className="flex gap-2">
            {[
              { path: '/dashboard', label: 'Dashboard' },
              { path: '/campaigns', label: 'Campaigns' },
              { path: '/analytics', label: 'Analytics' }
            ].map((tab) => (
              <button 
                key={tab.path} 
                onClick={() => navigate(tab.path)}
                className={`px-5 py-2 text-sm font-semibold rounded-xl transition-all duration-300 ${
                  currentPath.includes(tab.path)
                    ? 'text-primary bg-primary/10 shadow-sm' 
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4">
            {currentTaskId && status?.status === 'in_progress' && (
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest font-mono">Live</span>
              </div>
            )}
            <button className="text-slate-600 hover:text-slate-700 transition-colors relative">
              <Bell size={18} />
              <div className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-blue-500 rounded-full border border-[#0D0D1A]" />
            </button>
          </div>
        </header>

        {/* ── Main Content Area ── */}
        <div className="flex-1 flex overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/campaigns" replace />} />
            
            <Route path="/dashboard" element={
              <div className="flex-1 overflow-y-auto bg-[var(--bg-main)]">
                <DashboardView />
              </div>
            } />
            
            <Route path="/analytics" element={
              <div className="flex-1 overflow-y-auto bg-[var(--bg-main)]">
                <AnalyticsView />
              </div>
            } />

            <Route path="/campaigns/*" element={
              <>
                {/* Left Panel — only shown on content agent */}
                {activeAgent === 'content' && (
                  <div className="w-[420px] shrink-0 border-r border-[var(--border-main)] overflow-y-auto glass-panel bg-opacity-40">
                    <div className="p-8">
                      <div className="animate-in fade-in duration-500">
                        <CampaignBriefForm onSubmit={handleBriefSubmit} isLoading={loading} />
                      </div>
                    </div>
                  </div>
                )}

                {/* Right Panel */}
                <div className="flex-1 overflow-y-auto bg-[var(--bg-main)]">
                  {/* Non-content agents */}
                  {activeAgent !== 'content' && (
                    <div className="max-w-2xl mx-auto p-8 animate-in fade-in duration-500">
                      {activeAgent === 'strategy' && <StrategyView />}
                      {activeAgent === 'research' && <ResearchView />}
                      {activeAgent === 'saved' && <SavedView />}
                      {activeAgent === 'settings' && <SettingsView theme={theme} toggleTheme={toggleTheme} />}
                    </div>
                  )}

                  {/* Content agent */}
                  {activeAgent === 'content' && (
                    <>
                      {!currentTaskId ? (
                        <div className="h-full flex items-center justify-center p-8">
                          <div className="text-center max-w-xs">
                            <div className="w-16 h-16 rounded-2xl bg-primary/5 dark:bg-primary/10 border border-primary/10 dark:border-primary/20 flex items-center justify-center mx-auto mb-5 shadow-glow">
                              <Zap size={28} className="text-primary/70 dark:text-primary/90" />
                            </div>
                            <h3 className="text-lg font-bold text-[var(--text-main)] mb-2">Ready to launch</h3>
                            <p className="text-xs text-[var(--text-muted)] leading-relaxed">
                              Fill in your campaign brief and our 5 AI agents will generate your complete marketing package.
                            </p>
                            <div className="mt-6 grid grid-cols-5 gap-2">
                              {[
                                { label: 'Strategy', color: 'border-blue-500/20 text-blue-500/50' },
                                { label: 'Research', color: 'border-purple-500/20 text-purple-500/50' },
                                { label: 'Content', color: 'border-teal-500/20 text-teal-500/50' },
                                { label: 'Analytics', color: 'border-amber-500/20 text-amber-500/50' },
                                { label: 'Design', color: 'border-orange-500/20 text-orange-500/50' },
                              ].map((a) => (
                                <div key={a.label} className={`p-2 rounded-lg border ${a.color} text-center`}>
                                  <p className="text-[9px] font-bold uppercase tracking-tighter">{a.label}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ) : results ? (
                        <div className="p-6 pb-24 animate-in fade-in duration-700">
                          <ResultDisplay
                            content={results}
                            onDownload={handleDownloadAssets}
                            isDownloading={isDownloading}
                          />
                        </div>
                      ) : (
                        <div className="h-full w-full overflow-y-auto">
                          <LiveOrchestration status={status} isLoading={loading} error={error} />
                        </div>
                      )}
                    </>
                  )}
                </div>
              </>
            } />
          </Routes>
        </div>

        {/* ── Bottom Timeline ── */}
        <div className="h-16 glass-panel border-t border-[var(--border-main)] px-8 flex items-center justify-between z-30 shrink-0 transition-colors duration-300">
          <div className="flex items-center gap-3">
            {[
              { label: 'Generated', icon: CheckCircle2, active: results !== null },
              { label: 'Review & Edit', icon: Edit3, active: results !== null },
              { label: 'Approve & Publish', icon: Rocket, active: false },
            ].map((step, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-bold transition-all duration-300 ${
                  step.active
                    ? 'bg-primary/10 border-primary/30 text-primary shadow-sm'
                    : 'bg-[var(--bg-main)] border-[var(--border-main)] text-[var(--text-muted)]'
                }`}>
                  <step.icon size={15} />
                  {step.label}
                </div>
                {idx < 2 && <div className={`w-8 h-px ${step.active ? 'bg-primary/40' : 'bg-[var(--border-main)]'}`} />}
              </div>
            ))}
          </div>
          <div className="flex flex-col items-end">
             <span className="text-xs font-bold text-slate-800 dark:text-slate-200">AdPilot Engine</span>
             <span className="text-[9px] text-[var(--text-muted)] font-mono uppercase tracking-widest mt-0.5">Enterprise Architecture</span>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
