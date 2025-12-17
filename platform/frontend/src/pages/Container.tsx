import React, { useState } from 'react'
import { Container, AlertTriangle } from 'lucide-react'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useAuth } from '../contexts/AuthContext'
import { 
  GrypeSection, 
  TrivySection, 
  SyftSection, 
  KubeHunterSection, 
  KubeBenchSection, 
  KubescapeSection 
} from '../components/container'

const ContainerSecurity: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [activeTab, setActiveTab] = useState('trivy')

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
          <h1 className="text-2xl font-semibold text-gray-900">Container Security</h1>
          <p className="text-gray-500 mt-1">Security scanning for containers and Kubernetes</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-50 text-purple-600 rounded-lg text-sm font-medium">
          <Container className="w-4 h-4" />
          Container Tools
        </div>
      </div>

      {/* Advertencia de seguridad */}
      <div className="border border-purple-200 bg-purple-50 p-6 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-purple-600" />
          <h2 className="text-lg font-semibold text-purple-800">SECURITY WARNING</h2>
        </div>
        <div className="text-purple-700 space-y-2 text-sm">
          <p>• These tools are designed for authorized security testing only.</p>
          <p>• Unauthorized use may be illegal and have serious consequences.</p>
          <p>• Ensure you have explicit permission before scanning containers or Kubernetes clusters.</p>
        </div>
      </div>

      {/* Tabs principales */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Container Security Tools</h2>
          <p className="text-gray-500 text-sm">
            Select the tool to use
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-4 overflow-x-auto">
          {['trivy', 'grype', 'syft', 'kube-hunter', 'kube-bench', 'kubescape'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
            </button>
          ))}
        </div>

        {/* Contenido del tab activo */}
        <div className="mt-4">
          {activeTab === 'trivy' && currentWorkspace?.id && (
            <TrivySection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'grype' && currentWorkspace?.id && (
            <GrypeSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'syft' && currentWorkspace?.id && (
            <SyftSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'kube-hunter' && currentWorkspace?.id && (
            <KubeHunterSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'kube-bench' && currentWorkspace?.id && (
            <KubeBenchSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'kubescape' && currentWorkspace?.id && (
            <KubescapeSection workspaceId={currentWorkspace.id} />
          )}
        </div>
      </div>
    </div>
  )
}

export default ContainerSecurity

