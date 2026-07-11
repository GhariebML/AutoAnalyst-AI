import React, { useEffect, useState } from 'react'
import { CampaignBriefForm } from './CampaignBriefForm'
import { listAssets, getTaskStatus } from '../services/mockProvider'
import { BarChart2, Layers, Activity } from 'lucide-react'

export const Dashboard: React.FC = () => {
  const [assetsCount, setAssetsCount] = useState(0)
  const [status, setStatus] = useState<{ status: string; message?: string }>({ status: 'idle' })

  useEffect(() => {
    let mounted = true
    async function load() {
      const assets = await listAssets()
      if (!mounted) return
      setAssetsCount(assets.length)
    }
    load()
    const t = setInterval(async () => {
      const s = await getTaskStatus('demo')
      if (!mounted) return
      setStatus(s)
    }, 2000)
    return () => {
      mounted = false
      clearInterval(t)
    }
  }, [])

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 mission-panel relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl -mr-10 -mt-10 transition-transform group-hover:scale-150" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Active workflows</div>
              <div className="text-4xl font-black text-slate-900 dark:text-white">{assetsCount}</div>
            </div>
            <div className="p-3 bg-primary/10 border border-primary/20 rounded-2xl">
              <Layers className="text-primary w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="p-6 mission-panel relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-accent/5 rounded-full blur-2xl -mr-10 -mt-10 transition-transform group-hover:scale-150" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Running bots</div>
              <div className="text-4xl font-black text-slate-900 dark:text-white">164</div>
            </div>
            <div className="p-3 bg-accent/10 border border-accent/20 rounded-2xl">
              <Activity className="text-accent w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="p-6 mission-panel relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-2xl -mr-10 -mt-10 transition-transform group-hover:scale-150" />
          <div className="flex items-center justify-between relative z-10">
            <div>
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Tasks today</div>
              <div className="text-4xl font-black text-slate-900 dark:text-white">81,290</div>
            </div>
            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-2xl">
              <BarChart2 className="text-purple-500 w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Active Workflows */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-2 p-6 mission-panel">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Active workflows</h3>
            <button className="text-sm font-semibold text-primary bg-primary/10 hover:bg-primary/20 px-4 py-2 rounded-xl transition-colors">View all workflows</button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1,2,3].map((i)=> (
              <div key={i} className="p-5 glass-panel rounded-2xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group">
                <div className="text-sm font-bold text-slate-900 dark:text-slate-100 group-hover:text-primary transition-colors">Invoice Approval Automation</div>
                <div className="text-xs text-slate-500 mt-2 font-medium">Avg processing time: 2h 14m</div>
                <div className="mt-4 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)]" />
                  <span className="text-[11px] font-bold text-amber-500 uppercase tracking-wide">Risky</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 mission-panel flex flex-col">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">AI insight</h3>
          <div className="text-sm text-slate-500 font-medium">Bottleneck detected</div>
          
          <div className="mt-4 p-5 glass-panel border border-primary/20 rounded-2xl flex-1 flex flex-col justify-between relative overflow-hidden">
             <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-r from-primary to-purple-500" />
            <div className="text-sm text-slate-800 dark:text-slate-200 font-semibold leading-relaxed">Finance approval workflow exceeds SLA by 18%</div>
            <button className="mt-6 w-full bg-primary hover:bg-primary-hover text-white font-bold py-2.5 rounded-xl shadow-glow transition-all">Apply recommendation</button>
          </div>
        </div>
      </div>

      {/* Quick Start + Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-2 p-6 mission-panel">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-5">Quick Start</h3>
          <div className="max-w-xl">
             <CampaignBriefForm onSubmit={() => {}} isLoading={false} />
          </div>
        </div>

        <div className="p-6 mission-panel flex flex-col justify-center text-center">
          <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center mb-4 relative">
             <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-75" />
             <Activity className="text-primary w-8 h-8 relative z-10" />
          </div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Engine Status</h3>
          <div className="inline-flex items-center justify-center gap-2 px-4 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full mx-auto">
             <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
             <span className="text-xs font-bold text-green-600 dark:text-green-400 uppercase tracking-widest">{status.message || status.status}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
