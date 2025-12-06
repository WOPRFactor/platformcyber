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
        <p className="text-red-400">Debes iniciar sesión para acceder a esta página</p>
      </div>
    )
  }

  if (!currentWorkspace) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-yellow-400">Por favor selecciona un workspace</p>
      </div>
    )
  }

  return (
    <>
      <div className="container mx-auto px-4 py-8 space-y-6">
        <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
          <h1 className="text-3xl font-bold text-green-400 mb-2">Reconocimiento y OSINT</h1>
          <p className="text-green-600">
            Herramientas de reconocimiento pasivo y activo para recopilar información sobre objetivos
          </p>
      </div>
      
        {/* Información del workspace */}
        {currentWorkspace && (
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
              <h2 className="text-xl font-bold text-green-400">Workspace Actual</h2>
              <p className="text-green-600">
                {currentWorkspace.name} - {currentWorkspace.target_domain || 'Sin target configurado'}
              </p>
            </div>
            {currentWorkspace.target_domain ? (
            <div className="space-y-2">
              <p className="text-green-600 flex items-center gap-2">
                <span className="text-green-400">🎯</span>
                Target del workspace: <span className="text-green-300 font-mono font-bold">{currentWorkspace.target_domain}</span>
              </p>
              {currentWorkspace.target_ip && (
                <p className="text-gray-400 text-sm">
                  IP: <span className="text-gray-300 font-mono">{currentWorkspace.target_ip}</span>
                </p>
              )}
                </div>
          ) : (
            <p className="text-yellow-600">
              ⚠️ Este workspace no tiene un target configurado. Ingresa manualmente el objetivo.
            </p>
          )}
          </div>
        )}

        {/* Target Input */}
        <ReconTargetInput target={target} setTarget={setTarget} clearTarget={clearTarget} />

      {/* Tabs de herramientas */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-green-400">Herramientas de Reconocimiento</h2>
          <p className="text-green-600">
            Seleccione la categoría de herramientas a utilizar
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
