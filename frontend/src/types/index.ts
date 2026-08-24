export interface Dataset {
  id: string;
  filename: string;
  file_size_bytes: number;
  file_format: string;
  rows?: number;
  columns?: number;
  health_score?: number;
  created_at: string;
}

export interface DatasetPreview {
  id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  dtypes?: Record<string, string>;
  health_score: number;
  data_preview: Record<string, any>[];
  column_profiles: Record<string, any>;
}

export interface AgentAction {
  tool: string;
  status: 'ok' | 'error';
  duration_ms: number;
  summary: string;
}

export interface AgentFinding {
  category: string;
  fact: string;
  evidence: string;
  interpretation: string;
  recommendation?: string;
  confidence: number;
}

export interface AgentTelemetry {
  agent_name: string;
  status: 'idle' | 'active' | 'completed' | 'error' | 'paused_hitl';
  duration_ms: number;
  actions_taken?: AgentAction[];
  findings?: AgentFinding[];
  recommendations?: string[];
}

export interface AgentEvent {
  type: string;
  run_id?: string;
  agent_name?: string;
  message?: string;
  timestamp: string;
  data?: Record<string, any>;
}

export interface AnalysisRun {
  id: string;
  dataset_id: string;
  target_column?: string;
  model_task?: string;
  status: 'pending' | 'running' | 'paused_for_approval' | 'paused_hitl' | 'completed' | 'failed';
  champion_model_name?: string;
  champion_score?: number;
  executive_summary?: string;
  insights?: string[];
  findings?: AgentFinding[];
  profile?: Record<string, any>;
  evaluation?: Record<string, any>;
  model_results?: Record<string, any>;
  evaluation_results?: Record<string, any>;
  eda_results?: Record<string, any>;
  duration_ms?: number;
  report_path?: string;
  created_at: string;
}

export interface ChatMessage {
  id?: string;
  role?: 'user' | 'assistant';
  sender?: 'user' | 'assistant';
  content?: string;
  text?: string;
  timestamp: string;
  source?: string;
  suggested_followups?: string[];
}

export interface DashboardSummary {
  total_runs: number;
  completed_runs: number;
  running_runs: number;
  failed_runs: number;
  total_datasets: number;
  total_insights: number;
  total_models_trained: number;
  avg_quality_score: number;
  avg_duration_ms: number;
  champion_models: string[];
}

export interface RunTimelineItem {
  date: string;
  completed: number;
  running: number;
  failed: number;
  total: number;
}

export interface AgentActivitySummary {
  agent_name: string;
  display_name: string;
  category: string;
  total_executions: number;
  success_rate_pct: number;
  avg_duration_ms: number;
  tools_used: string[];
}

export interface ToolCatalogItem {
  name: string;
  description: string;
  category: string;
  tags: string[];
  version: string;
  is_autonomous: boolean;
}

export interface SubsystemHealth {
  name: string;
  status: string;
  latency_ms: number;
  details: string;
}

export interface FullSystemHealth {
  status: string;
  app_version: string;
  subsystems: SubsystemHealth[];
  llm_gateway: {
    provider: string;
    status: string;
    model: string;
    total_requests: number;
  };
  timestamp: string;
}
