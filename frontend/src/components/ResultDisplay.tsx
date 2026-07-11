import React, { useState } from 'react';
import {
  Copy, Download, Loader, Layout, Mail, Share2,
  ExternalLink, Sparkles, ChevronRight, ChevronDown, Check,
  Target, Calendar, Award, TrendingUp, Info
} from 'lucide-react';
import type { ContentOutput } from '../types';

interface ResultDisplayProps {
  content: ContentOutput | null;
  onDownload?: () => void;
  isDownloading?: boolean;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ content, onDownload, isDownloading }) => {
  const [expandedAdIdx, setExpandedAdIdx] = useState<number | null>(null);
  const [expandedEmailIdx, setExpandedEmailIdx] = useState<number | null>(null);
  const [expandedSocialIdx, setExpandedSocialIdx] = useState<number | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!content) return null;

  const handleCopyText = (e: React.MouseEvent, text: string, key: string) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="w-full space-y-6">

      {/* ── Header ── */}
      <div className="flex items-center justify-between p-1">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
            Campaign Intelligence <Sparkles className="text-primary w-5 h-5 animate-pulse" />
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Cooperative outputs generated across 5 autonomous marketing agents
          </p>
        </div>
        <button
          onClick={onDownload}
          disabled={isDownloading}
          className="px-5 py-2.5 bg-primary hover:bg-primary/90 disabled:bg-primary/50 text-white rounded-xl text-sm font-bold flex items-center gap-2 transition-all hover:scale-105 active:scale-95 shadow-glow"
        >
          {isDownloading ? <Loader className="animate-spin" size={16} /> : <Download size={16} />}
          {isDownloading ? 'Exporting Package...' : 'Export Campaign Brief'}
        </button>
      </div>

      {/* ── Ad Creatives (Content Agent) ── */}
      <div className="mission-panel overflow-hidden border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm">
        <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 bg-teal-50/50 dark:bg-teal-500/5 flex items-center gap-2">
          <div className="w-1.5 h-5 rounded-full bg-teal-500" />
          <Layout size={16} className="text-teal-500" />
          <h3 className="text-xs font-black uppercase tracking-widest text-teal-600 dark:text-teal-400">Ad Creatives & Copywriting</h3>
          <span className="ml-auto text-[10px] font-mono font-bold text-teal-600/60 dark:text-teal-400/40 uppercase tracking-widest">Content Agent</span>
        </div>
        
        <div className="p-5 space-y-4">
          <p className="text-xs text-slate-500 font-medium">Click on any ad creative card below to review copywriting structure, visual designs prompts, target audience focus, and performance estimates.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {content.ads.map((ad, idx) => {
              const isExpanded = expandedAdIdx === idx;
              const copyKey = `ad-body-${idx}`;
              return (
                <div 
                  key={idx} 
                  onClick={() => setExpandedAdIdx(isExpanded ? null : idx)}
                  className={`relative rounded-2xl border transition-all duration-300 overflow-hidden cursor-pointer shadow-sm ${
                    isExpanded 
                      ? 'md:col-span-3 bg-white dark:bg-[#161B22] border-teal-500/50 ring-1 ring-teal-500/20' 
                      : 'bg-gray-50 dark:bg-[#161B22]/50 hover:bg-white dark:hover:bg-[#161B22] border-gray-100 dark:border-gray-800/80 hover:border-teal-500/30'
                  }`}
                >
                  {/* Card Front Header */}
                  <div className="p-5 flex flex-col justify-between min-h-[140px] bg-gradient-to-br from-teal-50/30 dark:from-teal-500/5 to-gray-50/10 dark:to-gray-900/10">
                    <div className="flex items-center justify-between">
                      <span className="px-2.5 py-0.5 bg-teal-500/10 dark:bg-teal-500/20 rounded-full text-[10px] font-bold text-teal-600 dark:text-teal-400 uppercase tracking-wide border border-teal-500/10">
                        {ad.platform}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500 font-bold">
                        {ad.performance}
                      </span>
                    </div>
                    <div className="mt-4">
                      <h4 className="text-sm font-black text-slate-900 dark:text-slate-100 leading-snug line-clamp-2">
                        {ad.headline}
                      </h4>
                    </div>
                  </div>

                  {/* Card Bottom / Toggle Action */}
                  <div className="px-5 py-3.5 flex items-center justify-between border-t border-gray-100 dark:border-gray-800 bg-gray-50/30 dark:bg-black/5">
                    <span className="text-[11px] font-bold text-teal-600 dark:text-teal-400 uppercase tracking-widest flex items-center gap-1.5">
                      CTA: <span className="font-mono text-slate-700 dark:text-slate-300">{ad.cta}</span>
                    </span>
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={(e) => handleCopyText(e, `${ad.headline}\n\n${ad.body}`, copyKey)}
                        className="p-1 text-slate-600 dark:text-slate-400 hover:text-teal-500 transition-colors"
                        title="Copy ad copy"
                      >
                        {copiedKey === copyKey ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} />}
                      </button>
                      {isExpanded ? (
                        <ChevronDown size={14} className="text-teal-500" />
                      ) : (
                        <ChevronRight size={14} className="text-slate-700 group-hover:text-teal-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Content View */}
                  {isExpanded && (
                    <div className="p-6 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-[#0d1117] animate-in slide-in-from-top duration-300 space-y-6">
                      
                      {/* Copy Sections */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div className="space-y-2">
                          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block">Headline copy</span>
                          <div className="p-4 rounded-xl bg-gray-50 dark:bg-[#161B22] border border-gray-100 dark:border-gray-800 relative group/copy">
                            <p className="text-xs font-bold text-slate-900 dark:text-slate-100">{ad.headline}</p>
                            <button 
                              onClick={(e) => handleCopyText(e, ad.headline, 'head')}
                              className="absolute top-2 right-2 opacity-0 group-hover/copy:opacity-100 p-1 bg-white dark:bg-black/40 rounded border border-gray-150 dark:border-gray-700 text-slate-700 hover:text-primary transition-all"
                            >
                              {copiedKey === 'head' ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                            </button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block">Body Copy</span>
                          <div className="p-4 rounded-xl bg-gray-50 dark:bg-[#161B22] border border-gray-100 dark:border-gray-800 relative group/copy">
                            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">{ad.body}</p>
                            <button 
                              onClick={(e) => handleCopyText(e, ad.body, 'body')}
                              className="absolute top-2 right-2 opacity-0 group-hover/copy:opacity-100 p-1 bg-white dark:bg-black/40 rounded border border-gray-150 dark:border-gray-700 text-slate-700 hover:text-primary transition-all"
                            >
                              {copiedKey === 'body' ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Design Prompt & Concept */}
                      {ad.visualPrompt && (
                        <div className="space-y-2">
                          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block">DALL-E Visual Brief (Design Agent)</span>
                          <div className="p-4 rounded-xl bg-gradient-to-r from-teal-500/5 to-primary/5 border border-teal-500/10 dark:border-teal-500/20">
                            <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-mono">
                              {ad.visualPrompt}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Strategy Insights & Performance estimates */}
                      <div className="pt-2">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block mb-3">Targeting & Predictive Estimates</span>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-black/10 flex items-start gap-3">
                            <Target className="text-primary w-4.5 h-4.5 shrink-0 mt-0.5" />
                            <div>
                              <p className="text-[9px] uppercase tracking-wider font-bold text-slate-600">Target Segment</p>
                              <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-0.5 truncate max-w-[150px]">{ad.targetAudience || 'Core demographic'}</p>
                            </div>
                          </div>

                          <div className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-black/10 flex items-start gap-3">
                            <Award className="text-amber-500 w-4.5 h-4.5 shrink-0 mt-0.5" />
                            <div>
                              <p className="text-[9px] uppercase tracking-wider font-bold text-slate-600">Funnel Placement</p>
                              <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-0.5">{ad.funnelStage || 'Campaign goal'}</p>
                            </div>
                          </div>

                          <div className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-black/10 flex items-start gap-3">
                            <TrendingUp className="text-emerald-500 w-4.5 h-4.5 shrink-0 mt-0.5" />
                            <div>
                              <p className="text-[9px] uppercase tracking-wider font-bold text-slate-600">Forecasted CTR</p>
                              <p className="text-xs font-bold text-emerald-500 mt-0.5">{ad.ctrEstimate || '3.5%'}</p>
                            </div>
                          </div>

                          <div className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-black/10 flex items-start gap-3">
                            <Info className="text-teal-500 w-4.5 h-4.5 shrink-0 mt-0.5" />
                            <div>
                              <p className="text-[9px] uppercase tracking-wider font-bold text-slate-600">Avg. CPC Estimate</p>
                              <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-0.5">{ad.cpcEstimate || '$1.25'}</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Hashtags */}
                      {ad.hashtags && ad.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-2">
                          {ad.hashtags.map((tag, tIdx) => (
                            <span key={tIdx} className="px-2.5 py-1 bg-gray-50 dark:bg-[#161B22] border border-gray-150 dark:border-gray-800 rounded-lg text-[10px] font-semibold text-slate-700 dark:text-slate-300">
                              #{tag.replace('#', '')}
                            </span>
                          ))}
                        </div>
                      )}

                    </div>
                  )}

                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Two Columns: Email Sequences & CTAs ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Email Sequence (Strategy Agent) */}
        <div className="lg:col-span-7 mission-panel overflow-hidden border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 bg-primary/5 dark:bg-primary/10 flex items-center gap-2">
            <div className="w-1.5 h-5 rounded-full bg-primary" />
            <Mail size={16} className="text-primary" />
            <h3 className="text-xs font-black uppercase tracking-widest text-primary">Email Automations Sequence</h3>
            <span className="ml-auto text-[10px] font-mono font-bold text-primary/60 dark:text-primary/40 uppercase tracking-widest">Strategy Agent</span>
          </div>

          <div className="p-5 space-y-4">
            <p className="text-xs text-slate-500 font-medium">Click on any email sequence item below to expand the full subject, sequence schedule, onboarding trigger conditions, and copywriting content.</p>
            <div className="space-y-3">
              {content.emailSequences.map((email, idx) => {
                const isExpanded = expandedEmailIdx === idx;
                const copyKey = `email-body-${idx}`;
                return (
                  <div 
                    key={idx}
                    onClick={() => setExpandedEmailIdx(isExpanded ? null : idx)}
                    className={`rounded-2xl border transition-all duration-300 cursor-pointer overflow-hidden ${
                      isExpanded 
                        ? 'bg-white dark:bg-[#161B22] border-primary/40 ring-1 ring-primary/10' 
                        : 'bg-gray-50 dark:bg-[#161B22]/50 hover:bg-white dark:hover:bg-[#161B22] border-gray-100 dark:border-gray-800/80 hover:border-primary/20'
                    }`}
                  >
                    {/* Header */}
                    <div className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="px-2.5 py-1 bg-primary/10 dark:bg-primary/20 rounded-lg text-[10px] font-mono font-bold text-primary tracking-wide">
                          Day {email.sendDay || idx * 2 + 1}
                        </span>
                        <div>
                          <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 leading-tight">
                            {email.subject}
                          </h4>
                          {!isExpanded && (
                            <p className="text-[10px] text-slate-600 dark:text-slate-400 mt-1 max-w-[340px] truncate">
                              {email.preview}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={(e) => handleCopyText(e, `Subject: ${email.subject}\n\n${email.body}`, copyKey)}
                          className="p-1 text-slate-600 dark:text-slate-400 hover:text-primary transition-colors"
                          title="Copy email copy"
                        >
                          {copiedKey === copyKey ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                        </button>
                        {isExpanded ? (
                          <ChevronDown size={14} className="text-primary" />
                        ) : (
                          <ChevronRight size={14} className="text-slate-600" />
                        )}
                      </div>
                    </div>

                    {/* Expandable Email Details */}
                    {isExpanded && (
                      <div className="p-5 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-[#0d1117] animate-in slide-in-from-top duration-300 space-y-4">
                        
                        {/* Meta Settings */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 bg-gray-50 dark:bg-black/20 rounded-xl border border-gray-100 dark:border-gray-850 text-[10px]">
                          <div>
                            <span className="font-bold text-slate-600 block uppercase tracking-wide">Automation Trigger</span>
                            <span className="text-slate-800 dark:text-slate-300 mt-0.5 block leading-normal">{email.triggerCondition || 'Trigger condition'}</span>
                          </div>
                          <div>
                            <span className="font-bold text-slate-600 block uppercase tracking-wide">Sequence Goal</span>
                            <span className="text-slate-800 dark:text-slate-300 mt-0.5 block leading-normal">{email.goal || 'Conversion benchmark'}</span>
                          </div>
                          <div>
                            <span className="font-bold text-slate-600 block uppercase tracking-wide">Segment Focus</span>
                            <span className="text-slate-800 dark:text-slate-300 mt-0.5 block leading-normal truncate">{email.audienceFocus || 'Target audience'}</span>
                          </div>
                        </div>

                        {/* Subject & Preview */}
                        <div className="space-y-1">
                          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400">Subject line</span>
                          <p className="text-xs font-black text-slate-900 dark:text-slate-100">{email.subject}</p>
                        </div>

                        {/* Professional Email Client Mockup */}
                        <div className="space-y-2">
                          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block">Copywriting</span>
                          <div className="rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
                            {/* Window header */}
                            <div className="px-4 py-2.5 bg-gray-100 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-800 flex items-center gap-1.5">
                              <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
                              <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                              <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
                              <span className="ml-auto text-[9px] font-mono text-slate-500 uppercase tracking-widest">HTML Preview</span>
                            </div>
                            {/* Window body */}
                            <div className="p-5 bg-white dark:bg-[#161B22] text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans whitespace-pre-line">
                              {email.body}
                            </div>
                          </div>
                        </div>

                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* CTAs & Predictive Scores (Analytics Agent) */}
        <div className="lg:col-span-5 space-y-5 flex flex-col">
          
          {/* CTAs - Analytics */}
          <div className="mission-panel overflow-hidden border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm flex-1">
            <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 bg-amber-50/50 dark:bg-amber-500/5 flex items-center gap-2">
              <div className="w-1.5 h-5 rounded-full bg-amber-500" />
              <ExternalLink size={16} className="text-amber-500" />
              <h3 className="text-xs font-black uppercase tracking-widest text-amber-600 dark:text-amber-400">CTAs & Copy Variants</h3>
              <span className="ml-auto text-[10px] font-mono font-bold text-amber-600/60 dark:text-amber-400/40 uppercase tracking-widest">Analytics Agent</span>
            </div>
            
            <div className="p-5 space-y-4">
              <p className="text-xs text-slate-500 font-medium">Optimal call to action buttons sorted by conversion performance and CTR forecasts.</p>
              
              <div className="space-y-3">
                {[
                  { text: 'Get Started Now', score: 'High Intent', type: 'Primary Conversion Button', bg: 'bg-primary text-white border-primary shadow-lg shadow-primary/20' },
                  { text: 'Try for Free', score: 'Medium Intent', type: 'Secondary Trial Trigger', bg: 'bg-teal-500/10 border-teal-500/20 text-teal-600 dark:text-teal-400' },
                  { text: 'Schedule an Operations Audit', score: 'Educational', type: 'Consultation Qualifier', bg: 'bg-gray-50 dark:bg-[#161B22]/50 border-gray-100 dark:border-gray-800 text-slate-800 dark:text-slate-300' },
                  { text: 'Learn More', score: 'Awareness', type: 'Informational Funnel Stage', bg: 'bg-gray-50 dark:bg-[#161B22]/50 border-gray-100 dark:border-gray-800 text-slate-800 dark:text-slate-300' }
                ].map((cta, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800/80 bg-gray-50/20 dark:bg-black/5 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-slate-900 dark:text-slate-200">{cta.text}</p>
                      <p className="text-[9px] text-slate-500 mt-0.5 font-medium">{cta.type} · {cta.score}</p>
                    </div>
                    <button 
                      onClick={(e) => handleCopyText(e, cta.text, `cta-${idx}`)}
                      className="text-slate-600 dark:text-slate-400 hover:text-primary transition-colors ml-4"
                    >
                      {copiedKey === `cta-${idx}` ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* A/B Testing Strategy Widget */}
          <div className="mission-panel p-5 flex items-start gap-4 border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm bg-gradient-to-r from-amber-500/5 to-primary/5">
            <div className="p-3.5 bg-amber-500/10 border border-amber-500/20 rounded-2xl shrink-0">
              <Sparkles size={18} className="text-amber-500" />
            </div>
            <div>
              <p className="text-xs font-black text-slate-900 dark:text-slate-100 uppercase tracking-wider">A/B Testing Variants</p>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed mt-1">
                The Analytics Agent evaluates CTR and CPC in real-time. Turn on the **Real LLM Agent DAG** in Settings to generate specialized A/B alternative variations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Social Media Feed (Research Agent) ── */}
      <div className="mission-panel overflow-hidden border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm">
        <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 bg-purple-50/50 dark:bg-purple-500/5 flex items-center gap-2">
          <div className="w-1.5 h-5 rounded-full bg-purple-500" />
          <Share2 size={16} className="text-purple-500" />
          <h3 className="text-xs font-black uppercase tracking-widest text-purple-600 dark:text-purple-400">Social Media & Feed Calendar</h3>
          <span className="ml-auto text-[10px] font-mono font-bold text-purple-600/60 dark:text-purple-400/40 uppercase tracking-widest">Research Agent</span>
        </div>

        <div className="p-5 space-y-4">
          <p className="text-xs text-slate-500 font-medium">Click on any social media post card below to review platform schedules, best time to post recommendations, and creative visual generation guidelines.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {content.socialPosts.map((post, idx) => {
              const isExpanded = expandedSocialIdx === idx;
              const copyKey = `social-post-${idx}`;
              return (
                <div 
                  key={idx}
                  onClick={() => setExpandedSocialIdx(isExpanded ? null : idx)}
                  className={`rounded-2xl border transition-all duration-300 cursor-pointer overflow-hidden ${
                    isExpanded 
                      ? 'md:col-span-3 bg-white dark:bg-[#161B22] border-purple-500/50 ring-1 ring-purple-500/10' 
                      : 'bg-gray-50 dark:bg-[#161B22]/50 hover:bg-white dark:hover:bg-[#161B22] border-gray-100 dark:border-gray-800/80 hover:border-purple-500/20'
                  }`}
                >
                  {/* Card Front Header */}
                  <div className="p-5 bg-gradient-to-br from-purple-50/30 dark:from-purple-500/5 to-gray-50/10 dark:to-gray-900/10">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-600 dark:text-purple-400 font-black text-xs">
                        {post.platform[0]}
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          {post.platform} Post
                        </h4>
                        <p className="text-[9px] text-slate-500 uppercase tracking-widest mt-0.5">
                          {post.postType || 'Visual Content'}
                        </p>
                      </div>
                      <div className="ml-auto flex items-center gap-2">
                        <button 
                          onClick={(e) => handleCopyText(e, `${post.content}\n\n${post.hashtags.map(h => '#' + h.replace('#','')).join(' ')}`, copyKey)}
                          className="p-1 text-slate-600 dark:text-slate-400 hover:text-purple-500 transition-colors"
                          title="Copy social copy"
                        >
                          {copiedKey === copyKey ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                        </button>
                        {isExpanded ? (
                          <ChevronDown size={14} className="text-purple-500" />
                        ) : (
                          <ChevronRight size={14} className="text-slate-600" />
                        )}
                      </div>
                    </div>

                    <div className="mt-4">
                      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed line-clamp-3">
                        {post.content}
                      </p>
                    </div>
                  </div>

                  {/* Expanded Content View */}
                  {isExpanded && (
                    <div className="p-6 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-[#0d1117] animate-in slide-in-from-top duration-300 space-y-5">
                      
                      {/* Meta information */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-black/10 flex items-start gap-3">
                          <Calendar className="text-purple-500 w-4.5 h-4.5 mt-0.5 shrink-0" />
                          <div>
                            <p className="text-[9px] uppercase tracking-wider font-bold text-slate-600">Optimal Post Time</p>
                            <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-0.5">{post.bestTimeToPost || 'Tuesday morning'}</p>
                          </div>
                        </div>

                        <div className="p-3.5 rounded-xl border border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-black/10 flex items-start gap-3">
                          <Award className="text-purple-500 w-4.5 h-4.5 mt-0.5 shrink-0" />
                          <div>
                            <p className="text-[9px] uppercase tracking-wider font-bold text-slate-600">Content Category</p>
                            <p className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-0.5">{post.postType || 'Educational Post'}</p>
                          </div>
                        </div>
                      </div>

                      {/* Content copy */}
                      <div className="space-y-2">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block">Post Caption Copy</span>
                        <div className="p-4 rounded-xl bg-gray-50 dark:bg-[#161B22] border border-gray-100 dark:border-gray-800 relative group/copy">
                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">{post.content}</p>
                          <button 
                            onClick={(e) => handleCopyText(e, post.content, 'caption')}
                            className="absolute top-2 right-2 opacity-0 group-hover/copy:opacity-100 p-1 bg-white dark:bg-black/40 rounded border border-gray-150 dark:border-gray-700 text-slate-700 hover:text-primary transition-all"
                          >
                            {copiedKey === 'caption' ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                          </button>
                        </div>
                      </div>

                      {/* DALL-E Visual Prompts */}
                      {post.imagePrompt && (
                        <div className="space-y-2">
                          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-600 dark:text-slate-400 block">DALL-E Visual Brief (Design Agent)</span>
                          <div className="p-4 rounded-xl bg-gradient-to-r from-purple-500/5 to-primary/5 border border-purple-500/10 dark:border-purple-500/20">
                            <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-mono">
                              {post.imagePrompt}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Hashtags */}
                      <div className="flex flex-wrap gap-1.5 pt-2">
                        {post.hashtags.map((tag, tIdx) => (
                          <span key={tIdx} className="px-2.5 py-1 bg-purple-500/5 dark:bg-purple-500/10 border border-purple-500/10 dark:border-purple-500/20 rounded-lg text-[10px] font-semibold text-purple-600 dark:text-purple-400">
                            #{tag.replace('#', '')}
                          </span>
                        ))}
                      </div>

                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

    </div>
  );
};

export default ResultDisplay;
