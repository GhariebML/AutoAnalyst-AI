export interface CampaignBrief {
  businessName: string;
  productName: string;
  productDescription: string;
  targetAudience: string;
  goals: string[];
  budget: number;
  duration: string;
  tone: string;
}

export interface TaskResponse {
  taskId: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  message?: string;
}

export interface ContentOutput {
  ads: AdContent[];
  emailSequences: EmailSequence[];
  socialPosts: SocialPost[];
  summary?: string;
}

export interface AdContent {
  platform: string;
  headline: string;
  body: string;
  cta: string;
  performance?: string;
  targetAudience?: string;
  funnelStage?: string;
  adFormat?: string;
  visualPrompt?: string;
  hashtags?: string[];
  cpcEstimate?: string;
  ctrEstimate?: string;
}

export interface EmailSequence {
  subject: string;
  preview: string;
  body: string;
  sequence: number;
  sendDay?: number;
  triggerCondition?: string;
  goal?: string;
  audienceFocus?: string;
}

export interface SocialPost {
  platform: string;
  content: string;
  hashtags: string[];
  imagePrompt?: string;
  postType?: string;
  bestTimeToPost?: string;
  captionCopy?: string;
}

export interface DesignAsset {
  id: number;
  campaign_id: string;
  brief_json: Record<string, unknown>;
  image_url: string;
  created_at: string;
}

export interface DesignAssetsResponse {
  assets: DesignAsset[];
  total: number;
}
