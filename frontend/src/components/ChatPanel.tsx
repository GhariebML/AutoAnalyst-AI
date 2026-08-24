import React, { useState } from 'react';
import { ChatMessage } from '../types';
import { sendChatMessage } from '../api/client';
import {
  Send,
  User,
  Bot,
  Sparkles,
  Zap,
  Copy,
  Check,
} from 'lucide-react';

interface ChatPanelProps {
  analysisId: string | null;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ analysisId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      sender: 'assistant',
      content:
        'Hello! I am your Autonomous AI Analyst Copilot. Ask me any questions about the dataset schema, model leaderboard, feature drivers, or data cleaning transformations.',
      text: 'Hello! I am your Autonomous AI Analyst Copilot.',
      timestamp: new Date().toISOString(),
      suggested_followups: [
        'What are the strongest correlations in this dataset?',
        'Why was the champion ML model chosen over others?',
        'Which features have the highest predictive leverage?',
        'What data quality risks or anomalies should be addressed?',
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim() || !analysisId) return;

    const userMsg: ChatMessage = {
      role: 'user',
      sender: 'user',
      content: q,
      text: q,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const resp = await sendChatMessage(analysisId, q);
      const botMsg: ChatMessage = {
        role: 'assistant',
        sender: 'assistant',
        content: resp.response,
        text: resp.response,
        timestamp: resp.timestamp || new Date().toISOString(),
        suggested_followups: resp.suggested_followups,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          sender: 'assistant',
          content: 'Apologies, I encountered an error querying the dataset context. Please verify the backend connection and try again.',
          text: 'Error querying dataset.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <div className="glass-panel rounded-3xl border border-slate-800 flex flex-col h-[540px] overflow-hidden shadow-2xl animate-fadeIn">
      {/* Copilot Header */}
      <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-400 text-white shadow-glow-indigo">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-white">AI Analyst Copilot</h4>
              <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Grounded
              </span>
            </div>
            <p className="text-[10px] text-slate-400">Contextual dataset Q&A with zero hallucinations</p>
          </div>
        </div>

        <div className="text-[11px] font-mono text-slate-400">
          Run: <span className="text-slate-200 font-bold">{analysisId ? `#${analysisId.slice(0, 8)}` : 'None'}</span>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user' || msg.sender === 'user';
          const isCopied = copiedIdx === idx;
          const messageText = msg.content || msg.text || '';

          return (
            <div
              key={idx}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div
                className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                  isUser ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-cyan-400 border border-slate-700'
                }`}
              >
                {isUser ? <User className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
              </div>

              <div className={`space-y-2 max-w-[84%] ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                  className={`p-3.5 rounded-2xl text-xs leading-relaxed relative group ${
                    isUser
                      ? 'bg-indigo-600 text-white shadow-glow-indigo rounded-tr-none'
                      : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans">{messageText}</div>

                  {!isUser && (
                    <button
                      onClick={() => copyToClipboard(messageText, idx)}
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
                      title="Copy response"
                    >
                      {isCopied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  )}
                </div>

                {/* Suggested follow-up prompt chips */}
                {msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {msg.suggested_followups.map((sug, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => handleSend(sug)}
                        className="px-2.5 py-1 rounded-lg text-[10px] bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800 text-indigo-300 transition-all text-left flex items-center gap-1 group"
                      >
                        <Zap className="w-2.5 h-2.5 text-indigo-400 group-hover:scale-110 transition-transform shrink-0" />
                        <span>{sug}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-indigo-400 italic py-2">
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
            <span>Analyzing dataset context and formulating evidence...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 border-t border-slate-800 bg-slate-950/90 flex items-center gap-2"
      >
        <input
          type="text"
          placeholder={
            analysisId
              ? 'Ask anything about dataset trends, model rankings, or findings...'
              : 'Select or run an analysis first to activate copilot...'
          }
          disabled={!analysisId || isLoading}
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!inputQuery.trim() || !analysisId || isLoading}
          className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-glow-indigo disabled:opacity-50 transition-all shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
