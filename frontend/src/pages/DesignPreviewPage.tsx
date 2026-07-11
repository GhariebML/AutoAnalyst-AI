import React from 'react'
import { DesignPreview } from '../components/DesignPreview'

export const DesignPreviewPage: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-lg font-bold mb-4">Design Preview</h2>
      <DesignPreview campaignId="campaign-123" />
    </div>
  )
}

export default DesignPreviewPage
