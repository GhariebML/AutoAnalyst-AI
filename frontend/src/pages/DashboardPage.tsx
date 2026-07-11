import React from 'react'
import Dashboard from '../components/Dashboard'

export const DashboardPage: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-lg font-bold mb-4">Dashboard</h2>
      <Dashboard />
    </div>
  )
}

export default DashboardPage
