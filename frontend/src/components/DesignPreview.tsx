import { useEffect, useState } from 'react'
import { Download, Loader2, AlertCircle, Eye, Copy, Check } from 'lucide-react'
import { campaignService } from '../services/api'
import type { DesignAsset } from '../types'

interface DesignPreviewProps {
  campaignId: string | null
}

export function DesignPreview({ campaignId }: DesignPreviewProps) {
  const [assets, setAssets] = useState<DesignAsset[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState<DesignAsset | null>(null)
  const [copiedAssetId, setCopiedAssetId] = useState<number | null>(null)

  useEffect(() => {
    if (!campaignId) {
      setAssets([])
      setError(null)
      return
    }

    const fetchAssets = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await campaignService.getDesignAssets(campaignId)
        setAssets(response.assets || [])
      } catch (err) {
        setError(
          err instanceof Error ? `Failed to load design assets: ${err.message}` : 'Failed to load design assets'
        )
        setAssets([])
      } finally {
        setLoading(false)
      }
    }

    fetchAssets()
  }, [campaignId])

  const handleDownloadAll = async () => {
    if (!campaignId || isDownloading) return

    setIsDownloading(true)
    try {
      const blob = await campaignService.downloadDesignAssets(campaignId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `campaign-${campaignId}-assets.zip`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to download assets'
      )
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDownloadSingle = async (asset: DesignAsset) => {
    try {
      const filename = `asset-${asset.id}.png`
      const blob = await campaignService.downloadSingleAsset(asset.id, filename)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to download asset'
      )
    }
  }

  const handleCopyUrl = (asset: DesignAsset) => {
    navigator.clipboard.writeText(asset.image_url)
    setCopiedAssetId(asset.id)
    setTimeout(() => setCopiedAssetId(null), 2000)
  }

  if (!campaignId) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <p>Select or create a campaign to view design assets</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-[var(--bg-main)] overflow-hidden">
      {/* Header */}
      <div className="border-b border-[var(--border-main)] p-4 md:p-6 shrink-0 bg-[var(--bg-sidebar)]">
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <h2 className="text-lg md:text-xl font-bold text-[var(--text-main)]">
              Design Assets
            </h2>
            {assets.length > 0 && (
              <button
                onClick={handleDownloadAll}
                disabled={isDownloading}
                aria-label="Download all assets"
                className="flex items-center gap-2 px-3 md:px-4 py-2 bg-primary hover:bg-primary/90 disabled:bg-primary/50 disabled:cursor-not-allowed text-white rounded-lg transition-colors text-sm md:text-base"
              >
                {isDownloading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                <span className="hidden sm:inline">Download All</span>
                <span className="sm:hidden">Download</span>
              </button>
            )}
          </div>

          {assets.length > 0 && (
            <p className="text-xs md:text-sm text-slate-400">
              {assets.length} asset{assets.length !== 1 ? 's' : ''} available
            </p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto bg-[var(--bg-main)]">
        {loading && (
          <div className="flex items-center justify-center h-full">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <p className="text-slate-500">Loading design assets...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="p-4 md:p-6">
            <div className="flex items-center gap-3 p-3 md:p-4 bg-red-50 border border-red-100 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && assets.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-slate-400">No design assets available yet</p>
          </div>
        )}

        {!loading && !error && assets.length > 0 && (
          <div className="p-4 md:p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {assets.map((asset) => (
              <div
                key={asset.id}
                className="group relative bg-[var(--bg-surface)] border border-[var(--border-main)] hover:border-primary/30 rounded-lg overflow-hidden transition-all duration-200 shadow-sm"
              >
                {/* Image Container */}
                <div className="aspect-video bg-gray-50 overflow-hidden">
                  <img
                    src={asset.image_url}
                    alt={`Design asset ${asset.id}`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    loading="lazy"
                    onError={(e) => {
                      const img = e.target as HTMLImageElement
                      img.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22%3E%3Crect fill=%22%231a1a2e%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 font-size=%2220%22 fill=%22%23666%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22%3EImage Not Found%3C/text%3E%3C/svg%3E'
                    }}
                  />
                </div>

                {/* Overlay */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                  <button
                    onClick={() => setSelectedAsset(asset)}
                    className="p-2 bg-primary hover:bg-primary/90 rounded-full text-white transition-colors"
                    title="Preview"
                    aria-label="Preview asset"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDownloadSingle(asset)}
                    className="p-2 bg-slate-600 hover:bg-slate-700 rounded-full text-white transition-colors"
                    title="Download"
                    aria-label={`Save asset ${asset.id}`}
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>

                {/* Asset Info */}
                <div className="p-3 md:p-4 border-t border-[var(--border-main)]">
                  <p className="text-xs text-slate-600 truncate">
                    Asset #{asset.id}
                  </p>
                  <p className="text-xs text-slate-500 mt-1 truncate">
                    {new Date(asset.created_at).toLocaleDateString()}
                  </p>
                  <button
                    onClick={() => handleCopyUrl(asset)}
                    className="mt-2 flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors w-full"
                    title="Copy image URL"
                  >
                    {copiedAssetId === asset.id ? (
                      <>
                        <Check className="w-3 h-3" />
                        <span>Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span className="truncate">Copy URL</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Full Screen Preview Modal */}
      {selectedAsset && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedAsset(null)}
        >
          <div
            className="bg-[var(--bg-surface)] rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto shadow-2xl border border-[var(--border-main)]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-[var(--bg-surface)] border-b border-[var(--border-main)] px-4 py-3 flex items-center justify-between">
              <h3 className="text-sm font-bold text-[var(--text-main)]">
                Asset #{selectedAsset.id}
              </h3>
              <button
                onClick={() => setSelectedAsset(null)}
                className="text-slate-500 hover:text-slate-700 transition-colors"
                aria-label="Close preview"
              >
                ✕
              </button>
            </div>

            <div className="p-4">
              <img
                src={selectedAsset.image_url}
                alt={`Design asset ${selectedAsset.id}`}
                className="w-full rounded-lg"
              />
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between p-3 bg-[var(--bg-main)] border border-[var(--border-main)] rounded-lg">
                  <span className="text-xs text-[var(--text-muted)]">URL</span>
                  <button
                    onClick={() => handleCopyUrl(selectedAsset)}
                    className="text-xs text-primary hover:text-primary/80 transition-colors"
                  >
                    {copiedAssetId === selectedAsset.id ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <button
                  onClick={() => handleDownloadSingle(selectedAsset)}
                  className="w-full px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Asset
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
