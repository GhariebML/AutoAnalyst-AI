import React, { useState } from 'react'

export const SettingsForm: React.FC = () => {
  const [openaiKey, setOpenaiKey] = useState('')
  const [cloudinaryKey, setCloudinaryKey] = useState('')

  const handleSave = () => {
    // For scaffold: persist to localStorage
    localStorage.setItem('OPENAI_API_KEY', openaiKey)
    localStorage.setItem('CLOUDINARY_API_KEY', cloudinaryKey)
    alert('Settings saved (local only)')
  }

  return (
    <div className="p-4 bg-slate-900 rounded">
      <div className="mb-3 font-bold">Integrations</div>
      <div className="space-y-3">
        <div>
          <label className="text-xs text-slate-400">OpenAI API Key</label>
          <input value={openaiKey} onChange={(e) => setOpenaiKey(e.target.value)} className="w-full mt-1 p-2 rounded bg-slate-800" />
        </div>
        <div>
          <label className="text-xs text-slate-400">Cloudinary API Key</label>
          <input value={cloudinaryKey} onChange={(e) => setCloudinaryKey(e.target.value)} className="w-full mt-1 p-2 rounded bg-slate-800" />
        </div>
        <div className="pt-2">
          <button onClick={handleSave} className="px-3 py-2 bg-blue-600 rounded font-bold">Save</button>
        </div>
      </div>
    </div>
  )
}

export default SettingsForm
