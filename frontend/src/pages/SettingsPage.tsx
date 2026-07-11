import React from 'react'
import SettingsForm from '../components/SettingsForm'

export const SettingsPage: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-lg font-bold mb-4">Settings</h2>
      <SettingsForm />
    </div>
  )
}

export default SettingsPage
