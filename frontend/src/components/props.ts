// Component prop interfaces and shared types for frontend scaffolding

export interface CampaignFormProps {
  onSubmit: (taskId: string) => void
  isLoading?: boolean
}

export interface TaskRow {
  id: string
  campaignId?: string
  name: string
  status: string
  progress?: number
}

export interface TaskListProps {
  tasks: TaskRow[]
  onSelect?: (id: string) => void
}

export interface AssetCardProps {
  assetId: string
  url: string
  width?: number
  height?: number
  style?: string
  onDownload?: (id: string) => void
}

export interface CampaignDetailProps {
  campaignId: string
}

export interface DesignPreviewProps {
  assetId: string
  onApprove?: (id: string) => void
  onRegenerate?: (id: string) => void
}

export interface SettingsProps {
  onSave?: () => void
}
