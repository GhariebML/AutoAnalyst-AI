import { Dataset, DatasetPreview, AnalysisRun } from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function uploadDatasetFile(file: File): Promise<Dataset> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/datasets`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function fetchDatasets(): Promise<Dataset[]> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error('Failed to fetch datasets');
  return res.json();
}

export async function fetchDatasetPreview(datasetId: string): Promise<DatasetPreview> {
  const res = await fetch(`${API_BASE}/datasets/${datasetId}/preview`);
  if (!res.ok) throw new Error('Failed to fetch dataset preview');
  return res.json();
}

export async function createAnalysisRun(params: {
  dataset_id: string;
  target_column?: string;
  model_task?: string;
  require_approval?: boolean;
}): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE}/analyses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to start analysis');
  }
  return res.json();
}

export async function fetchAnalysisRun(analysisId: string): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE}/analyses/${analysisId}`);
  if (!res.ok) throw new Error('Failed to fetch analysis run');
  return res.json();
}

export async function fetchAnalyses(): Promise<AnalysisRun[]> {
  const res = await fetch(`${API_BASE}/analyses`);
  if (!res.ok) throw new Error('Failed to fetch analyses');
  return res.json();
}

export async function approveHITL(
  runId: string,
  approved: boolean,
  _modifications?: Record<string, any>
): Promise<AnalysisRun> {
  const res = await fetch(`${API_BASE}/runs/${runId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ step: 'cleaning', approved }),
  });
  if (!res.ok) throw new Error('Failed to submit approval');
  return res.json();
}

export async function sendChatMessage(
  analysisId: string,
  query: string
): Promise<{ response: string; source: string; suggested_followups: string[]; timestamp?: string }> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis_id: analysisId, query }),
  });
  if (!res.ok) throw new Error('Failed to send chat query');
  const data = await res.json();
  return {
    ...data,
    timestamp: data.timestamp || new Date().toISOString(),
  };
}

export function subscribeToRunEvents(
  runId: string,
  onMessage: (event: any) => void,
  onError?: (err: any) => void
): () => void {
  const eventSource = new EventSource(`${API_BASE}/runs/${runId}/events`);

  eventSource.onmessage = (e) => {
    try {
      const parsed = JSON.parse(e.data);
      onMessage(parsed);
    } catch {
      onMessage({ type: 'MESSAGE', message: e.data, timestamp: new Date().toISOString() });
    }
  };

  eventSource.onerror = (e) => {
    if (onError) onError(e);
    eventSource.close();
  };

  return () => eventSource.close();
}

// Aliases
export const fetchAnalysis = fetchAnalysisRun;
export const createAnalysis = (datasetId: string, targetCol?: string, _mode?: string) =>
  createAnalysisRun({ dataset_id: datasetId, target_column: targetCol });
export const approveHITLPlan = approveHITL;

export async function fetchDashboardSummary() {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  if (!res.ok) throw new Error('Failed to fetch dashboard summary');
  return res.json();
}

export async function fetchRunsTimeline(days = 7) {
  const res = await fetch(`${API_BASE}/dashboard/runs-timeline?days=${days}`);
  if (!res.ok) throw new Error('Failed to fetch runs timeline');
  return res.json();
}

export async function fetchAgentsActivity() {
  const res = await fetch(`${API_BASE}/dashboard/agents-activity`);
  if (!res.ok) throw new Error('Failed to fetch agents activity');
  return res.json();
}

export async function fetchToolsCatalog() {
  const res = await fetch(`${API_BASE}/system/tools`);
  if (!res.ok) throw new Error('Failed to fetch tools catalog');
  return res.json();
}

export async function fetchFullSystemHealth() {
  const res = await fetch(`${API_BASE}/system/health`);
  if (!res.ok) throw new Error('Failed to fetch system health');
  return res.json();
}

export async function fetchLLMHealth() {
  const res = await fetch(`${API_BASE}/system/llm/health`);
  if (!res.ok) throw new Error('Failed to fetch LLM health');
  return res.json();
}
