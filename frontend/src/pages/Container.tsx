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
      <div className="container mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Por favor selecciona un workspace para continuar</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Container Security</h1>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Container className="w-4 h-4" />
          Security scanning para contenedores y Kubernetes
        </div>
      </div>

      {/* Advertencia de seguridad */}
      <div className="border border-purple-500 bg-purple-50 p-6 rounded-lg">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-purple-600" />
          <h2 className="text-xl font-bold text-purple-800">ADVERTENCIA DE SEGURIDAD</h2>
        </div>
        <div className="text-purple-700 space-y-2">
          <p>• Estas herramientas están diseñadas para pruebas de seguridad autorizadas únicamente.</p>
          <p>• El uso no autorizado puede ser ilegal y tener consecuencias graves.</p>
          <p>• Asegúrese de tener permiso explícito antes de escanear contenedores o clusters Kubernetes.</p>
        </div>
      </div>

      {/* Tabs principales */}
      <div className="bg-gray-800 border border-purple-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-purple-400">Herramientas de Container Security</h2>
          <p className="text-purple-600 text-sm">
            Seleccione la herramienta a utilizar
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-purple-500 mb-4 overflow-x-auto">
          {['trivy', 'grype', 'syft', 'kube-hunter', 'kube-bench', 'kubescape'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
                activeTab === tab
                  ? 'border-purple-400 text-purple-400'
                  : 'border-transparent text-gray-400 hover:text-purple-400'
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

