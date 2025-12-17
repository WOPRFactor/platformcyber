/**
 * Reconnaissance Page
 * ===================
 * 
 * Página de reconocimiento y OSINT con interfaz mejorada.
 * 
 * Características:
 * - Tabs horizontales para categorías de herramientas
 * - Integración con todas las herramientas del backend
 * - Progreso en tiempo real
 * - Reconocimiento completo automatizado
 * 
 * Refactorizado: 2025-12-04
 */

import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useTarget } from '../contexts/TargetContext'
import { ReconnaissanceTabs } from './Reconnaissance/components/shared/ReconnaissanceTabs'
import { ReconTargetInput } from './Reconnaissance/components/shared/ReconTargetInput'
import { useCommandPreview } from './VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../components/CommandPreviewModal'
import { BasicReconSection } from './Reconnaissance/components/tools/BasicReconSection'
import { OSINTSection } from './Reconnaissance/components/tools/OSINTSection'
import { WebCrawlingSection } from './Reconnaissance/components/tools/WebCrawlingSection'
import { SecretsDetectionSection } from './Reconnaissance/components/tools/SecretsDetectionSection'
import { CompleteReconSection } from './Reconnaissance/components/tools/CompleteReconSection'

const Reconnaissance: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const { target, setTarget, clearTarget } = useTarget()
  const [activeTab, setActiveTab] = useState('basic')
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview } = commandPreview

  // Auto-completar target desde workspace - SIEMPRE actualizar cuando cambia el workspace
  useEffect(() => {
    if (currentWorkspace?.target_domain) {
      // Siempre actualizar el target cuando cambia el workspace
      setTarget(currentWorkspace.target_domain)
      console.log(`🎯 Target actualizado desde workspace: ${currentWorkspace.target_domain}`)
    } else if (currentWorkspace && !currentWorkspace.target_domain) {
      // Si el workspace no tiene target, limpiar el campo
      setTarget('')
      console.log(`⚠️ Workspace sin target configurado`)
    }
  }, [currentWorkspace?.id, currentWorkspace?.target_domain, setTarget])

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500">You must log in to access this page</p>
      </div>
    )
  }

  if (!currentWorkspace) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-amber-500">Please select a workspace</p>
      </div>
    )
  }

  return (
    <>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 shadow-sm">
          <h1 className="text-2xl font-semibold text-gray-900 mb-1">Reconnaissance & OSINT</h1>
          <p className="text-gray-500">
            Passive and active reconnaissance tools for gathering target information
          </p>
        </div>
      
        {/* Workspace Info */}
        {currentWorkspace && (
          <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 shadow-sm">
            <div className="mb-3">
              <h2 className="text-lg font-semibold text-gray-900">Current Workspace</h2>
              <p className="text-gray-500 text-sm">
                {currentWorkspace.name} - {currentWorkspace.target_domain || 'No target configured'}
              </p>
            </div>
            {currentWorkspace.target_domain ? (
              <div className="space-y-2">
                <p className="text-gray-600 flex items-center gap-2">
                  <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                  Workspace target: <span className="text-gray-900 font-mono font-medium">{currentWorkspace.target_domain}</span>
                </p>
                {currentWorkspace.target_ip && (
                  <p className="text-gray-500 text-sm">
                    IP: <span className="text-gray-700 font-mono">{currentWorkspace.target_ip}</span>
                  </p>
                )}
              </div>
            ) : (
              <p className="text-amber-600 flex items-center gap-2 text-sm">
                <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
                This workspace has no target configured. Enter the target manually.
              </p>
            )}
          </div>
        )}

        {/* Target Input */}
        <ReconTargetInput target={target} setTarget={setTarget} clearTarget={clearTarget} />

        {/* Tabs de herramientas */}
        <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 shadow-sm">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Reconnaissance Tools</h2>
            <p className="text-gray-500 text-sm mt-1">
              Select the tool category to use
            </p>
          </div>
        
          <div className="w-full">
            <ReconnaissanceTabs activeTab={activeTab} setActiveTab={setActiveTab} />

            {/* Contenido de cada tab */}
            {activeTab === 'basic' && (
              <BasicReconSection target={target} workspaceId={currentWorkspace.id} commandPreview={commandPreview} />
            )}

            {activeTab === 'osint' && (
              <OSINTSection target={target} workspaceId={currentWorkspace.id} commandPreview={commandPreview} />
            )}

            {activeTab === 'web' && (
              <WebCrawlingSection target={target} workspaceId={currentWorkspace.id} commandPreview={commandPreview} />
            )}

            {activeTab === 'secrets' && (
              <SecretsDetectionSection workspaceId={currentWorkspace.id} commandPreview={commandPreview} />
            )}

            {activeTab === 'complete' && (
              <CompleteReconSection target={target} workspaceId={currentWorkspace.id} />
            )}
          </div>
        </div>
      </div>
    
      <CommandPreviewModal
        isOpen={showPreview}
        onClose={closePreview}
        onExecute={executePreview}
        previewData={previewData}
        toolName={previewToolName}
        category="reconnaissance"
      />
    </>
  )
}

export default Reconnaissance
