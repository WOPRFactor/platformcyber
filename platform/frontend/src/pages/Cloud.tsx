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
        <h1 className="text-3xl font-bold text-white">Cloud Pentesting</h1>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <CloudIcon className="w-4 h-4" />
          Pentesting para entornos cloud (AWS, Azure, GCP)
        </div>
      </div>

      {/* Advertencia de seguridad */}
      <div className="border border-blue-500 bg-blue-50 p-6 rounded-lg">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-bold text-blue-800">ADVERTENCIA DE SEGURIDAD</h2>
        </div>
        <div className="text-blue-700 space-y-2">
          <p>• Estas herramientas están diseñadas para pruebas de penetración éticas y autorizadas únicamente.</p>
          <p>• El uso no autorizado puede ser ilegal y tener consecuencias graves.</p>
          <p>• Asegúrese de tener permiso explícito antes de ejecutar cualquier scan en entornos cloud.</p>
        </div>
      </div>

      {/* Tabs principales */}
      <div className="bg-gray-800 border border-blue-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-blue-400">Herramientas Cloud</h2>
          <p className="text-blue-600 text-sm">
            Seleccione la herramienta y proveedor cloud a utilizar
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-blue-500 mb-4 overflow-x-auto">
          {['pacu', 'scoutsuite', 'prowler', 'azurehound', 'roadtools'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
                activeTab === tab
                  ? 'border-blue-400 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-blue-400'
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

