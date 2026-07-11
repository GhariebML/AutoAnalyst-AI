import axios from 'axios';
import type { CampaignBrief, TaskResponse, ContentOutput, DesignAssetsResponse } from '../types';

const API_BASE = (import.meta.env.VITE_API_URL as string) || 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

// Attach JWT token from localStorage if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('adpilot_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Surface error messages — FastAPI 422 returns detail as an array of objects
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err?.response?.data?.detail;
    let message: string;
    if (Array.isArray(detail)) {
      // Pydantic validation errors: [{loc, msg, type}, ...]
      message = detail
        .map((d: { loc?: string[]; msg?: string }) =>
          d.loc ? `${d.loc.slice(1).join(' → ')}: ${d.msg}` : (d.msg ?? 'Validation error')
        )
        .join(' | ');
    } else if (typeof detail === 'string') {
      message = detail;
    } else {
      message = err?.message ?? 'Unknown error';
    }
    return Promise.reject(new Error(message));
  }
);

// ─── Service API ────────────────────────────────────────────────────────────

// ─── Service API ────────────────────────────────────────────────────────────

export const campaignService = {
  /** Submit a new campaign brief — calls the full multi-agent DAG pipeline. */
  async submitCampaign(brief: CampaignBrief): Promise<TaskResponse> {
    const response = await apiClient.post('/campaigns', brief);
    return response.data;
  },

  /** Poll campaign task status. */
  async getTaskStatus(taskId: string): Promise<TaskResponse> {
    const response = await apiClient.get(`/tasks/${taskId}`);
    return response.data;
  },

  /** Retrieve full campaign content results. */
  async getCampaignContent(campaignId: string): Promise<ContentOutput> {
    const response = await apiClient.get(`/campaigns/${campaignId}/content`);
    return response.data;
  },

  /** Download a ZIP of all design assets for a campaign. */
  async downloadDesignAssets(campaignId: string): Promise<Blob> {
    const response = await apiClient.get(
      `/campaigns/${campaignId}/design-assets/download`,
      { responseType: 'blob' }
    );
    return response.data;
  },

  /** Fetch design asset metadata for a campaign. */
  async getDesignAssets(campaignId: string): Promise<DesignAssetsResponse> {
    const response = await apiClient.get(`/campaigns/${campaignId}/design-assets`);
    return response.data;
  },

  /** Download a single design asset file by ID. */
  async downloadSingleAsset(assetId: number, _filename: string): Promise<Blob> {
    const response = await apiClient.get(`/design-assets/${assetId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default apiClient;
