import React from 'react'
import CampaignDetails from '../components/CampaignDetails'

export const CampaignDetailsPage: React.FC = () => {
  // For scaffold we leave campaignId optional
  return (
    <div className="p-6">
      <h2 className="text-lg font-bold mb-4">Campaign Details</h2>
      <CampaignDetails />
    </div>
  )
}

export default CampaignDetailsPage
