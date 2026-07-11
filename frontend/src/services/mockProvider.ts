// Richer mock data provider for local UI development (HD images, KPIs, departments)

import type { CampaignBrief, ContentOutput, DesignAsset } from '../types'

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export interface Department {
  id: string
  name: string
  owner: string
  health: 'healthy' | 'at_risk' | 'critical'
  campaigns: number
}

const sampleContent: ContentOutput = {
  ads: [
    {
      platform: 'LinkedIn',
      headline: 'Make more time for what matters',
      body: 'Automate content and design generation with AI-driven workflows.',
      cta: 'Get started',
    },
    {
      platform: 'Instagram',
      headline: 'Smart workflows for growing teams',
      body: 'Close more deals with on-brand creative assets delivered fast.',
      cta: 'Launch campaign',
    },
  ],
  emailSequences: [],
  socialPosts: [],
  summary: 'Mock campaign content for local dashboard previews.',
}

const sampleAssets: DesignAsset[] = [
  {
    id: 1,
    campaign_id: 'campaign-123',
    brief_json: { style: 'photorealistic', width: 1600, height: 900 },
    image_url: 'https://images.unsplash.com/photo-1506765515384-028b60a970df?w=1600&q=80&auto=format&fit=crop',
    created_at: '2026-05-19T09:00:00Z',
  },
  {
    id: 2,
    campaign_id: 'campaign-123',
    brief_json: { style: 'flat-illustration', width: 1600, height: 900 },
    image_url: 'https://images.unsplash.com/photo-1503602642458-232111445657?w=1600&q=80&auto=format&fit=crop',
    created_at: '2026-05-19T09:10:00Z',
  },
]

const departments: Department[] = [
  { id: 'd1', name: 'Marketing', owner: 'A. Hassan', health: 'healthy', campaigns: 12 },
  { id: 'd2', name: 'Product', owner: 'L. Omar', health: 'at_risk', campaigns: 5 },
  { id: 'd3', name: 'Sales', owner: 'R. Ali', health: 'critical', campaigns: 2 },
]

export async function submitCampaign(brief: CampaignBrief) {
  void brief
  return new Promise<{ taskId: string }>((resolve) =>
    setTimeout(() => resolve({ taskId: 'task-' + Date.now() }), 250)
  )
}

export async function getTaskStatus(taskId: string) {
  void taskId
  const t = Date.now() % 12000
  if (t < 4000) return { status: 'in_progress' as TaskStatus, message: 'Running strategy agent' }
  if (t < 9000) return { status: 'in_progress' as TaskStatus, message: 'Creating content & designs' }
  return { status: 'completed' as TaskStatus, message: 'All agents finished' }
}

export async function getCampaignContent(campaignId: string) {
  void campaignId
  await new Promise((r) => setTimeout(r, 300))
  return sampleContent
}

export async function listAssets(campaignId?: string) {
  await new Promise((r) => setTimeout(r, 150))
  return sampleAssets.filter((a) => !campaignId || a.campaign_id === campaignId)
}

export async function downloadDesignAssets(campaignId: string) {
  void campaignId
  const blob = new Blob(['dummy zip content'], { type: 'application/zip' })
  return blob
}

export async function listDepartments() {
  await new Promise((r) => setTimeout(r, 120))
  return departments
}

export async function getKPIs() {
  await new Promise((r) => setTimeout(r, 80))
  return {
    impressions: 124_392,
    clicks: 5_832,
    ctr: 4.7,
    conversions: 452,
  }
}
