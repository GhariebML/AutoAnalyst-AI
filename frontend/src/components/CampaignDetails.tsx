import React, { useEffect, useState } from 'react'
import { getCampaignContent, listAssets } from '../services/mockProvider'
import type { ContentOutput, DesignAsset } from '../types'

interface Props {
  campaignId?: string
}

export const CampaignDetails: React.FC<Props> = ({ campaignId }) => {
  const [content, setContent] = useState<ContentOutput | null>(null)
  const [assets, setAssets] = useState<DesignAsset[]>([])

  useEffect(() => {
    let mounted = true

    async function load() {
      if (!campaignId) return

      const c = await getCampaignContent(campaignId)
      const a = await listAssets(campaignId)
      if (!mounted) return

      setContent(c)
      setAssets(a)
    }

    load()
    return () => {
      mounted = false
    }
  }, [campaignId])

  return (
    <div>
      <h3 className="text-lg font-semibold mb-3">Campaign Outputs</h3>
      {!content && <div className="text-sm text-slate-400">No content yet for this campaign.</div>}
      {content && (
        <div className="space-y-4">
          <div>
            <h4 className="font-bold">Ad Content</h4>
            <ul className="list-disc ml-5">
              {content.ads.map((ad, i) => (
                <li key={`${ad.platform}-${i}`}>
                  <strong>{ad.headline}</strong> - {ad.body}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-bold">Summary</h4>
            <div>{content.summary || 'No summary available.'}</div>
          </div>
        </div>
      )}

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-3">Assets</h3>
        {assets.length === 0 && <div className="text-sm text-slate-400">No assets yet.</div>}
        <div className="grid grid-cols-3 gap-3">
          {assets.map((asset) => (
            <div key={asset.id} className="p-2 bg-slate-900 rounded">
              <img
                src={asset.image_url}
                alt={`Asset ${asset.id}`}
                className="w-full h-36 object-cover rounded"
              />
              <div className="mt-2 text-xs text-slate-400">
                {String(asset.brief_json.style || 'design')} - {String(asset.brief_json.width || 'auto')}x
                {String(asset.brief_json.height || 'auto')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default CampaignDetails
