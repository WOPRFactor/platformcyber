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
          <h1 className="text-2xl font-semibold text-gray-900">Active Directory</h1>
          <p className="text-gray-500 mt-1">Pentesting for Active Directory environments</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-orange-50 text-orange-600 rounded-lg text-sm font-medium">
          <Shield className="w-4 h-4" />
          AD Tools
        </div>
      </div>

      {/* Advertencia de seguridad */}
      <div className="border border-red-200 bg-red-50 p-6 rounded-xl">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          <h2 className="text-lg font-semibold text-red-800">CRITICAL SECURITY WARNING</h2>
        </div>
        <div className="text-red-700 space-y-2 text-sm">
          <p>• These operations can cause permanent damage to Active Directory domains.</p>
          <p>• Unauthorized use is illegal and may have serious consequences.</p>
          <p>• Ensure you have explicit written permission before running any tool.</p>
          <p>• These tools are designed only for authorized ethical penetration testing.</p>
        </div>
      </div>

      {/* Tabs principales */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Active Directory Tools</h2>
          <p className="text-gray-500 text-sm">
            Select the tool to use
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-4 overflow-x-auto">
          {['kerbrute', 'getnpusers', 'ldapdomaindump', 'adidnsdump', 'crackmapexec'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
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

