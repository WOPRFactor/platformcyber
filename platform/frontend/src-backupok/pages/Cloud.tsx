import React, { useState } from 'react'
import { Cloud as CloudIcon, AlertTriangle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import { 
  PacuSection, 
  ScoutSuiteSection, 
  ProwlerSection, 
  AzureHoundSection, 
  ROADtoolsSection 
} from '../components/cloud'

const Cloud: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [activeTab, setActiveTab] = useState('pacu')

  if (!currentWorkspace?.id) {
    return (
      <div className="p-6">
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-amber-800">Please select a workspace to continue</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Cloud Security</h1>
          <p className="text-gray-500 mt-1">Pentesting for cloud environments (AWS, Azure, GCP)</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium">
          <CloudIcon className="w-4 h-4" />
          Cloud Tools
        </div>
      </div>

      {/* Advertencia de seguridad */}
      <div className="border border-blue-200 bg-blue-50 p-6 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-blue-600" />
          <h2 className="text-lg font-semibold text-blue-800">SECURITY WARNING</h2>
        </div>
        <div className="text-blue-700 space-y-2 text-sm">
          <p>• These tools are designed for ethical and authorized penetration testing only.</p>
          <p>• Unauthorized use may be illegal and have serious consequences.</p>
          <p>• Ensure you have explicit permission before running any scan in cloud environments.</p>
        </div>
      </div>

      {/* Tabs principales */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Cloud Tools</h2>
          <p className="text-gray-500 text-sm">
            Select the tool and cloud provider to use
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-4 overflow-x-auto">
          {['pacu', 'scoutsuite', 'prowler', 'azurehound', 'roadtools'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Contenido del tab activo */}
        <div className="mt-4">
          {activeTab === 'pacu' && currentWorkspace?.id && (
            <PacuSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'scoutsuite' && currentWorkspace?.id && (
            <ScoutSuiteSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'prowler' && currentWorkspace?.id && (
            <ProwlerSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'azurehound' && currentWorkspace?.id && (
            <AzureHoundSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'roadtools' && currentWorkspace?.id && (
            <ROADtoolsSection workspaceId={currentWorkspace.id} />
          )}
        </div>
      </div>
    </div>
  )
}

export default Cloud

