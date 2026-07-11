import React from 'react';
import {
  Target, Search, LayoutDashboard, Settings, Lock,
  BookOpen, TrendingUp, Users, Lightbulb, Clock,
  Palette, BarChart2, Bookmark, Trash2, Download,
  Sun, Moon, Globe, Shield, Activity, DollarSign,
  MousePointerClick, Megaphone, Zap
} from 'lucide-react';

/* ─────────────────────────────────────
   Reusable Components
───────────────────────────────────── */

const Phase2Badge = () => (
  <span className="px-2 py-0.5 text-[9px] font-bold rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-400 font-mono uppercase tracking-widest">
    Phase 2
  </span>
);

const ComingSoonCard: React.FC<{ icon: React.ElementType; label: string; description: string; color: string }> = ({
  icon: Icon, label, description, color,
}) => (
  <div className="mission-panel p-4 flex items-center gap-4 hover:shadow-lg dark:hover:shadow-primary/5 transition-all duration-200 border border-gray-100 dark:border-gray-800 hover:border-gray-200 dark:hover:border-gray-700 group">
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${color} group-hover:scale-110 transition-transform`}>
      <Icon size={18} />
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-slate-700 dark:group-hover:text-slate-300 transition-colors">{label}</p>
      <p className="text-xs text-slate-600 dark:text-slate-400 group-hover:text-slate-500 leading-snug transition-colors">{description}</p>
    </div>
    <Phase2Badge />
  </div>
);

const SectionHeader: React.FC<{ icon: React.ElementType; title: string; subtitle: string; color: string }> = ({
  icon: Icon, title, subtitle, color,
}) => (
  <div className="mb-6 pb-4 border-b border-gray-100 dark:border-gray-800">
    <div className="flex items-center gap-3 mb-2">
      <Icon size={20} className={`${color} group-hover:scale-110 transition-transform`} />
      <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">{title}</h2>
    </div>
    <p className="text-xs text-slate-600 dark:text-slate-400 ml-7">{subtitle}</p>
  </div>
);

/* ─────────────────────────────────────
   Dashboard Overview View (Top Tab)
───────────────────────────────────── */
export const DashboardView: React.FC = () => (
  <div className="w-full space-y-4 max-w-4xl mx-auto p-8 animate-in fade-in duration-500">
    <SectionHeader
      icon={Activity}
      title="Platform Overview"
      subtitle="High-level metrics across all AI-generated campaigns"
      color="text-emerald-400"
    />
    
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {[
        { label: 'Active Campaigns', value: '12', change: '+3', icon: Megaphone, color: 'text-blue-400', bg: 'bg-blue-500/10' },
        { label: 'Total Ad Spend', value: '$45.2k', change: '+12%', icon: DollarSign, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
        { label: 'Avg. Conversion', value: '3.8%', change: '+0.4%', icon: MousePointerClick, color: 'text-purple-400', bg: 'bg-purple-500/10' },
        { label: 'Agents Running', value: '5/5', change: 'Optimal', icon: Zap, color: 'text-amber-400', bg: 'bg-amber-500/10' },
      ].map((stat, i) => (
        <div key={i} className="mission-panel p-5 space-y-3 hover:border-primary/20 transition-colors">
          <div className="flex items-center justify-between">
            <div className={`p-2 rounded-lg ${stat.bg} ${stat.color}`}>
              <stat.icon size={16} />
            </div>
            <span className="text-[10px] font-bold text-emerald-400">{stat.change}</span>
          </div>
          <div>
            <p className="text-2xl font-black text-slate-900 dark:text-slate-100">{stat.value}</p>
            <p className="text-[10px] text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider">{stat.label}</p>
          </div>
        </div>
      ))}
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ComingSoonCard icon={BarChart2} label="Performance Graph" description="Visual breakdown of campaign ROI over time" color="bg-slate-500/10 border-slate-500/20 text-slate-400" />
      <ComingSoonCard icon={Users} label="Top Demographics" description="Best performing audience segments across channels" color="bg-slate-500/10 border-slate-500/20 text-slate-400" />
    </div>
  </div>
);

/* ─────────────────────────────────────
   Analytics View (Top Tab)
───────────────────────────────────── */
export const AnalyticsView: React.FC = () => (
  <div className="w-full space-y-4 max-w-4xl mx-auto p-8 animate-in fade-in duration-500">
    <SectionHeader
      icon={BarChart2}
      title="Campaign Analytics"
      subtitle="Deep dive into individual channel performance"
      color="text-amber-400"
    />
    <div className="mission-panel p-5 border-l-4 border-l-amber-500 mb-6">
      <div className="flex items-start gap-3 mb-4">
        <BarChart2 size={16} className="text-amber-400 mt-0.5 shrink-0" />
        <div>
          <p className="text-xs font-bold text-amber-600 dark:text-amber-400 mb-1">Analytics Agent</p>
          <p className="text-[11px] text-[var(--text-muted)] leading-relaxed">
            The Analytics Agent forecasts performance metrics, suggests budget reallocation based on real-time data, and provides A/B test variations to maximize ROI.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-4">
        {['ROI Forecasting', 'Budget Optimization', 'A/B Test Analysis', 'Channel Attribution', 'CAC Tracking', 'LTV Projections'].map((item) => (
          <div key={item} className="flex items-center gap-2 p-2 rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-100 dark:border-amber-500/20">
            <div className="w-1 h-1 rounded-full bg-amber-400 shrink-0" />
            <p className="text-[10px] text-[var(--text-muted)]">{item}</p>
          </div>
        ))}
      </div>
    </div>
    <div className="space-y-4">
      <ComingSoonCard icon={LayoutDashboard} label="Real-time Custom Dashboards" description="Build custom reporting views" color="bg-amber-500/10 border-amber-500/20 text-amber-400" />
      <ComingSoonCard icon={Target} label="Goal Tracking Alerts" description="Automated notifications when campaigns hit milestones" color="bg-amber-500/10 border-amber-500/20 text-amber-400" />
    </div>
  </div>
);

/* ─────────────────────────────────────
   Strategy Insights View
───────────────────────────────────── */
export const StrategyView: React.FC = () => (
  <div className="w-full space-y-4">
    <SectionHeader
      icon={Target}
      title="Strategy Insights"
      subtitle="Campaign positioning, objectives & tactical plan"
      color="text-blue-400"
    />
    <div className="mission-panel p-5 border-l-4 border-l-blue-500 hover:border-l-blue-400 transition-colors duration-200">
      <div className="flex items-start gap-3 mb-5">
        <Target size={16} className="text-blue-400 mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-bold text-blue-600 dark:text-blue-400 mb-2">Strategy Agent</p>
          <p className="text-xs text-[var(--text-muted)] leading-relaxed">
            The Strategy Agent analyzes your campaign brief and generates a comprehensive marketing strategy including brand positioning, competitive differentiation, target audience segments, and tactical channel recommendations.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 mt-4">
        {['Brand Positioning', 'Market Segmentation', 'Channel Mix', 'Budget Allocation', 'Timeline Planning', 'KPI Definition', 'Message Strategy'].map((item) => (
          <div key={item} className="flex items-center gap-2 p-3 rounded-lg bg-blue-500/8 dark:bg-blue-500/10 border border-blue-500/20 hover:bg-blue-500/15 hover:border-blue-500/40 hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-150 cursor-pointer group">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0 group-hover:bg-blue-300 transition-colors" />
            <p className="text-xs text-slate-600 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-slate-100 transition-colors font-medium">{item}</p>
          </div>
        ))}
      </div>
    </div>
    <ComingSoonCard icon={TrendingUp} label="SWOT Analysis" description="AI-generated strengths, weaknesses, opportunities, threats" color="bg-blue-500/10 border-blue-500/20 text-blue-400" />
    <ComingSoonCard icon={Lightbulb} label="Strategic Recommendations" description="Data-driven campaign strategy with priority ranking" color="bg-blue-500/10 border-blue-500/20 text-blue-400" />
    <ComingSoonCard icon={BookOpen} label="Playbook Generator" description="Full marketing playbook export as PDF" color="bg-blue-500/10 border-blue-500/20 text-blue-400" />
    <div className="p-3 rounded-xl border border-dashed border-white/15 bg-slate-500/5 text-center hover:bg-slate-500/10 transition-colors">
      <p className="text-xs text-slate-500 font-mono uppercase tracking-widest">Strategy outputs available after campaign generation</p>
    </div>
  </div>
);

/* ─────────────────────────────────────
   Audience Research View
───────────────────────────────────── */
export const ResearchView: React.FC = () => (
  <div className="w-full space-y-4">
    <SectionHeader
      icon={Search}
      title="Audience Research"
      subtitle="Market intelligence, competitor analysis & audience data"
      color="text-purple-400"
    />
    <div className="mission-panel p-5 border-l-4 border-l-purple-500 hover:border-l-purple-400 transition-colors duration-200">
      <div className="flex items-start gap-3 mb-5">
        <Search size={16} className="text-purple-400 mt-0.5 shrink-0" />
        <div>
          <p className="text-sm font-bold text-purple-600 mb-2">Research Agent</p>
          <p className="text-xs text-slate-400 leading-relaxed">
            The Research Agent gathers live market intelligence using SerpAPI, analyzes competitor campaigns, identifies audience pain points, and extracts trending topics to ensure your campaign is data-driven.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 mt-4">
        {['Competitor Mapping', 'Audience Personas', 'Trend Analysis', 'Keyword Research', 'Pain Point ID', 'Market Sizing'].map((item) => (
          <div key={item} className="flex items-center gap-2 p-3 rounded-lg bg-purple-500/8 border border-purple-500/20 hover:bg-purple-500/15 hover:border-purple-500/40 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-150 cursor-pointer group">
            <div className="w-1.5 h-1.5 rounded-full bg-purple-400 shrink-0 group-hover:bg-purple-300 transition-colors" />
            <p className="text-xs text-slate-300 group-hover:text-slate-100 transition-colors font-medium">{item}</p>
          </div>
        ))}
      </div>
    </div>
    <ComingSoonCard icon={Users} label="Audience Personas" description="AI-generated buyer persona profiles with psychographics" color="bg-purple-500/10 border-purple-500/20 text-purple-400" />
    <ComingSoonCard icon={Globe} label="Live Market Data" description="Real-time market research via SerpAPI integration" color="bg-purple-500/10 border-purple-500/20 text-purple-400" />
    <ComingSoonCard icon={TrendingUp} label="Competitor Intelligence" description="Automated competitor ad and content monitoring" color="bg-purple-500/10 border-purple-500/20 text-purple-400" />
    <div className="p-3 rounded-xl border border-dashed border-white/15 bg-slate-500/5 text-center hover:bg-slate-500/10 transition-colors">
      <p className="text-xs text-slate-500 font-mono uppercase tracking-widest">Research outputs available after campaign generation</p>
    </div>
  </div>
);

/* ─────────────────────────────────────
   Saved Content View
───────────────────────────────────── */
const mockSaved = [
  { name: 'FutureCorp — NeuralLink v2', date: '2026-05-10', status: 'Completed', color: 'text-teal-400' },
  { name: 'BioSync Health — Premium Plan', date: '2026-05-09', status: 'Completed', color: 'text-teal-400' },
  { name: 'CloudFleet — Enterprise SaaS', date: '2026-05-08', status: 'Draft', color: 'text-amber-400' },
];

export const SavedView: React.FC = () => (
  <div className="w-full space-y-4">
    <SectionHeader
      icon={LayoutDashboard}
      title="Saved Content"
      subtitle="Your previously generated campaigns"
      color="text-slate-400"
    />
    <div className="space-y-2">
      {mockSaved.map((item, idx) => (
        <div key={idx} className="mission-panel p-4 flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-gray-50 border border-gray-100 flex items-center justify-center shrink-0">
            <Bookmark size={14} className="text-slate-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-bold text-slate-900 truncate">{item.name}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <Clock size={10} className="text-slate-700" />
              <p className="text-[10px] text-slate-600 font-mono">{item.date}</p>
              <span className={`text-[9px] font-bold uppercase tracking-widest ${item.color}`}>{item.status}</span>
            </div>
          </div>
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button className="p-1.5 rounded-lg hover:bg-gray-100 text-slate-600 hover:text-slate-900 transition-colors"><Download size={13} /></button>
            <button className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-600 hover:text-red-400 transition-colors"><Trash2 size={13} /></button>
          </div>
        </div>
      ))}
    </div>
    <ComingSoonCard icon={Shield} label="Campaign Persistence" description="PostgreSQL/MongoDB storage for permanent history" color="bg-slate-500/10 border-slate-500/20 text-slate-400" />
  </div>
);

/* ─────────────────────────────────────
   Settings View
───────────────────────────────────── */
export const SettingsView: React.FC<{ theme: string; toggleTheme: () => void }> = ({ theme, toggleTheme }) => (
  <div className="w-full space-y-4">
    <SectionHeader
      icon={Settings}
      title="Settings"
      subtitle="Configure your AdPilot workspace"
      color="text-slate-400"
    />

    {/* Theme */}
    <div className="mission-panel p-5 space-y-3">
      <p className="text-[10px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-widest">Appearance</p>
      
      {/* Dark Mode */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Moon size={16} className={theme === 'dark' ? 'text-blue-400' : 'text-slate-400'} />
          <div>
            <p className="text-xs font-bold text-slate-900 dark:text-slate-100">Dark Mode</p>
            <p className="text-[10px] text-slate-600 dark:text-slate-400">Mission control theme</p>
          </div>
        </div>
        <div 
          onClick={() => theme !== 'dark' && toggleTheme()}
          className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${theme === 'dark' ? 'bg-blue-600' : 'bg-[var(--border-main)]'}`}
        >
          <div className={`absolute top-0.5 w-4 h-4 bg-[var(--bg-main)] rounded-full shadow transition-all ${theme === 'dark' ? 'right-0.5' : 'left-0.5'}`} />
        </div>
      </div>

      {/* Light Mode */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Sun size={16} className={theme === 'light' ? 'text-amber-500' : 'text-slate-400'} />
          <div>
            <p className="text-xs font-bold text-[var(--text-main)]">Light Mode</p>
            <p className="text-[10px] text-[var(--text-muted)]">Standard bright theme</p>
          </div>
        </div>
        <div 
          onClick={() => theme !== 'light' && toggleTheme()}
          className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${theme === 'light' ? 'bg-amber-500' : 'bg-[var(--border-main)]'}`}
        >
          <div className={`absolute top-0.5 w-4 h-4 bg-[var(--bg-main)] rounded-full shadow transition-all ${theme === 'light' ? 'right-0.5' : 'left-0.5'}`} />
        </div>
      </div>
    </div>

    {/* API Keys */}
    <div className="mission-panel p-5 space-y-3 border border-[var(--border-main)] bg-[var(--bg-card)]">
      <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest">API Configuration</p>
      {[
        { label: 'OpenAI API Key', placeholder: 'sk-••••••••••••••••', icon: Lock },
        { label: 'SerpAPI Key', placeholder: '••••••••••••••••', icon: Globe },
      ].map((field) => (
        <div key={field.label}>
          <label className="block text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-1.5">{field.label}</label>
          <div className="relative">
            <field.icon size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-700" />
            <input
              type="password"
              placeholder={field.placeholder}
              className="w-full bg-[var(--bg-main)] border border-[var(--border-main)] rounded-lg pl-9 pr-3 py-2 text-xs text-[var(--text-main)] focus:outline-none focus:border-primary/50 placeholder:text-[var(--text-muted)]"
            />
          </div>
        </div>
      ))}
      <button className="w-full py-2 bg-primary/10 border border-primary/20 text-primary text-xs font-bold rounded-lg hover:bg-primary/20 transition-all">
        Save API Keys
      </button>
    </div>

    {/* Agent Config */}
    <div className="mission-panel p-5 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Agent Configuration</p>
        <Phase2Badge />
      </div>
      {[
        { label: 'LLM Model', value: 'GPT-4o', icon: Lightbulb },
        { label: 'Design Engine', value: 'DALL·E 3', icon: Palette },
        { label: 'Analytics Mode', value: 'Predictive', icon: BarChart2 },
      ].map((item) => (
        <div key={item.label} className="flex items-center justify-between opacity-50">
          <div className="flex items-center gap-2">
            <item.icon size={14} className="text-slate-600" />
            <p className="text-[11px] text-slate-500">{item.label}</p>
          </div>
          <span className="text-[10px] text-slate-600 font-mono">{item.value}</span>
        </div>
      ))}
    </div>

    {/* About */}
    <div className="p-4 rounded-xl border border-[var(--border-main)] bg-[var(--bg-sidebar)] text-center space-y-1">
      <p className="text-xs font-bold text-[var(--text-main)]">AdPilot v2.4.0</p>
      <p className="text-[10px] text-[var(--text-muted)]">Multi-Agent Marketing Platform · Phase 2</p>
      <p className="text-[10px] text-[var(--text-muted)] font-mono">Built by @GhariebML · @Sleem13</p>
    </div>
  </div>
);
