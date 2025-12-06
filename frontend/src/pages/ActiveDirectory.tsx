import React, { useState } from 'react'
import { Shield, AlertTriangle } from 'lucide-react'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useAuth } from '../contexts/AuthContext'
import { 
  KerbruteSection, 
  GetNPUsersSection, 
  LDAPDomainDumpSection, 
  ADIDNSDumpSection, 
  CrackMapExecSection 
} from '../components/activeDirectory'

const ActiveDirectory: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [activeTab, setActiveTab] = useState('kerbrute')

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
        <h1 className="text-3xl font-bold text-white">Active Directory</h1>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Shield className="w-4 h-4" />
          Pentesting para entornos Active Directory
        </div>
      </div>

      {/* Advertencia de seguridad */}
      <div className="border border-red-500 bg-red-50 p-6 rounded-lg">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          <h2 className="text-xl font-bold text-red-800">⚠️ ADVERTENCIA CRÍTICA DE SEGURIDAD</h2>
        </div>
        <div className="text-red-700 space-y-2">
          <p>• Estas operaciones pueden causar daño permanente al dominio Active Directory.</p>
          <p>• El uso no autorizado es ilegal y puede tener consecuencias graves.</p>
          <p>• Asegúrese de tener permiso explícito y autorización escrita antes de ejecutar cualquier herramienta.</p>
          <p>• Estas herramientas están diseñadas únicamente para pruebas de penetración éticas autorizadas.</p>
        </div>
      </div>

      {/* Tabs principales */}
      <div className="bg-gray-800 border border-red-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-red-400">Herramientas de Active Directory</h2>
          <p className="text-red-600 text-sm">
            Seleccione la herramienta a utilizar
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-red-500 mb-4 overflow-x-auto">
          {['kerbrute', 'getnpusers', 'ldapdomaindump', 'adidnsdump', 'crackmapexec'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap ${
                activeTab === tab
                  ? 'border-red-400 text-red-400'
                  : 'border-transparent text-gray-400 hover:text-red-400'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Contenido del tab activo */}
        <div className="mt-4">
          {activeTab === 'kerbrute' && currentWorkspace?.id && (
            <KerbruteSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'getnpusers' && currentWorkspace?.id && (
            <GetNPUsersSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'ldapdomaindump' && currentWorkspace?.id && (
            <LDAPDomainDumpSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'adidnsdump' && currentWorkspace?.id && (
            <ADIDNSDumpSection workspaceId={currentWorkspace.id} />
          )}
          {activeTab === 'crackmapexec' && currentWorkspace?.id && (
            <CrackMapExecSection workspaceId={currentWorkspace.id} />
          )}
        </div>
      </div>
    </div>
  )
}

export default ActiveDirectory

