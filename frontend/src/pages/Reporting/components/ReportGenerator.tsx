/**
 * Report Generator Component
 * Componente simple para generar reportes
 */

import React, { useState } from 'react'
import { BarChart3, Target, Shield, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'
import { useWorkspace } from '../../../contexts/WorkspaceContext'
import ExecutiveReportModal from './ExecutiveReportModal'

interface ReportGeneratorProps {
  activeTab: string
  complianceStandard: string
  executiveMutation: UseMutationResult<any, any, any>
  technicalMutation: UseMutationResult<any, any, any>
  complianceMutation: UseMutationResult<any, any, any>
  startDate?: string
  endDate?: string
  onReportGenerated?: (report: any) => void
  currentWorkspaceId?: number
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  activeTab,
  complianceStandard,
  executiveMutation,
  technicalMutation,
  complianceMutation,
  startDate,
  endDate,
  onReportGenerated,
  currentWorkspaceId
}) => {
  const { currentWorkspace } = useWorkspace()
  
  // Estados para controlar el modal
  const [showReportModal, setShowReportModal] = useState(false)
  const [reportData, setReportData] = useState<any>(null)
  
  // Usar useRef para mantener referencia estable al callback
  const onReportGeneratedRef = React.useRef(onReportGenerated)
  
  React.useEffect(() => {
    onReportGeneratedRef.current = onReportGenerated
    console.log('🔄 ReportGenerator - onReportGenerated actualizado:', {
      has: !!onReportGenerated,
      type: typeof onReportGenerated,
      currentWorkspaceId
    })
  }, [onReportGenerated, currentWorkspaceId])

  const handleExecutiveClick = () => {
    if (!currentWorkspace || !currentWorkspace.id) {
      console.error('❌ No hay workspace seleccionado')
      return
    }
    const params = {
      workspaceId: currentWorkspace.id,
      startDate: startDate || undefined,
      endDate: endDate || undefined
    }
    console.log('🚀 Calling executiveMutation.mutate with params:', params)
    executiveMutation.mutate(params, {
      onSuccess: (response) => {
        console.log('✅ Executive mutation success:', response)
        if (response.success && response.data) {
          console.log('🔓 Abriendo modal con datos del reporte')
          console.log('📊 Datos del reporte:', JSON.stringify(response.data, null, 2))
          setReportData(response.data)
          setShowReportModal(true)
          
          // También llamar al callback si existe
          if (onReportGeneratedRef.current) {
            onReportGeneratedRef.current(response.data)
          }
        } else {
          console.warn('⚠️ Response no tiene success o data:', response)
        }
      },
      onError: (error) => {
        console.error('❌ Error en handleExecutiveClick:', error)
      }
    })
  }

  const handleTechnicalClick = () => {
    if (!currentWorkspace || !currentWorkspace.id) {
      console.error('❌ No hay workspace seleccionado')
      return
    }
    const params = {
      workspaceId: currentWorkspace.id,
      startDate: startDate || undefined,
      endDate: endDate || undefined
    }
    technicalMutation.mutate(params, {
      onSuccess: (response) => {
        console.log('✅ Technical mutation success:', response)
        if (response.success && response.data) {
          console.log('🔓 Abriendo modal con datos del reporte técnico')
          setReportData(response.data)
          setShowReportModal(true)
          
          if (onReportGeneratedRef.current) {
            onReportGeneratedRef.current(response.data)
          }
        }
      }
    })
  }

  const handleComplianceClick = () => {
    if (!currentWorkspace || !currentWorkspace.id) {
      console.error('❌ No hay workspace seleccionado')
      return
    }
    const params = {
      workspaceId: currentWorkspace.id,
      standard: complianceStandard,
      startDate: startDate || undefined,
      endDate: endDate || undefined
    }
    complianceMutation.mutate(params, {
      onSuccess: (response) => {
        console.log('✅ Compliance mutation success:', response)
        if (response.success && response.data) {
          console.log('🔓 Abriendo modal con datos del reporte de cumplimiento')
          setReportData(response.data)
          setShowReportModal(true)
          
          if (onReportGeneratedRef.current) {
            onReportGeneratedRef.current(response.data)
          }
        }
      }
    })
  }

  return (
    <div className="w-full">
      {activeTab === 'executive' && (
        <div className="mt-4">
          <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Resumen Ejecutivo
              </h3>
              <p className="text-red-600">
                Reporte de alto nivel para stakeholders y directivos
              </p>
            </div>
            <button
              type="button"
              onClick={handleExecutiveClick}
              disabled={executiveMutation.isPending}
              className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {executiveMutation.isPending ? (
                <Loader className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <BarChart3 className="w-4 h-4 mr-2" />
              )}
              Generar Resumen Ejecutivo
            </button>
          </div>
        </div>
      )}

      {activeTab === 'technical' && (
        <div className="mt-4">
          <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                <Target className="w-5 h-5" />
                Reporte Técnico Detallado
              </h3>
              <p className="text-red-600">
                Reporte técnico completo con todos los hallazgos y metodología
              </p>
            </div>
            <button
              type="button"
              onClick={handleTechnicalClick}
              disabled={technicalMutation.isPending}
              className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {technicalMutation.isPending ? (
                <Loader className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Target className="w-4 h-4 mr-2" />
              )}
              Generar Reporte Técnico
            </button>
          </div>
        </div>
      )}

      {activeTab === 'compliance' && (
        <div className="mt-4">
          <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Reporte de Cumplimiento - {complianceStandard.toUpperCase()}
              </h3>
              <p className="text-red-600">
                Evaluación de cumplimiento con estándares de seguridad específicos
              </p>
            </div>
            <button
              type="button"
              onClick={handleComplianceClick}
              disabled={complianceMutation.isPending}
              className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {complianceMutation.isPending ? (
                <Loader className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Shield className="w-4 h-4 mr-2" />
              )}
              Generar Reporte de Cumplimiento
            </button>
          </div>
        </div>
      )}

      {/* Modal para mostrar el reporte generado */}
      {showReportModal && reportData && (
        <ExecutiveReportModal 
          isOpen={showReportModal}
          onClose={() => {
            console.log('🚪 Cerrando modal de reporte')
            setShowReportModal(false)
            setReportData(null)
          }}
          reportData={reportData}
          workspaceName={currentWorkspace?.name}
        />
      )}
    </div>
  )
}

export default ReportGenerator

