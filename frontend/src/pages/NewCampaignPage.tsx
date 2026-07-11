import React from 'react'
import { CampaignBriefForm } from '../components/CampaignBriefForm'

export const NewCampaignPage: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-lg font-bold mb-4">New Campaign</h2>
      <div className="max-w-2xl bg-slate-900 p-4 rounded">
        <CampaignBriefForm onSubmit={() => {}} />
      </div>
    </div>
  )
}

export default NewCampaignPage
