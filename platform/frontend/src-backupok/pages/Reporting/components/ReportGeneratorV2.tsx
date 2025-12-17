/**
 * Report Generator V2 Component
 * Componente para generar reportes usando el nuevo módulo V2
 */

import React, { useState } from 'react'
import { FileText, Loader, CheckCircle, XCircle, AlertCircle, Download } from 'lucide-react'
import { useWorkspace } from '../../../contexts/WorkspaceContext'
import { reportingAPI } from '../../../lib/api/reporting'
import { toast } from 'sonner'
import { useReportV2Progress } from '../hooks/useReportV2Progress'
import { useConsole } from '../../../contexts/ConsoleContext'

interface ReportGeneratorV2Props {
  onReportGenerated?: (report: any) => void
}

const ReportGeneratorV2: React.FC<ReportGeneratorV2Props> = ({
  onReportGenerated
}) => {
  const { currentWorkspace } = useWorkspace()
  const { startTask, updateTaskProgress, completeTask, failTask } = useConsole()
  const [reportType, setReportType] = useState<'technical' | 'executive' | 'compliance'>('technical')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  
  // Ref para mantener el taskId de la consola (debe estar fuera del useEffect)
  const consoleTaskIdRef = React.useRef<string | null>(null)
  
  const { status, isPolling } = useReportV2Progress(taskId)

  // Actualizar progreso en la consola cuando cambia el status
  React.useEffect(() => {
    if (!status || !taskId) return

    // DEBUG: Ver qué llega en el status
    console.log('🔍 Status recibido:', JSON.stringify(status, null, 2))

    if (status.status === 'processing' && status.progress !== undefined) {
      if (!consoleTaskIdRef.current) {
        // Crear tarea en consola
        const consoleTaskId = startTask(
          'Reporting',
          `Generando reporte ${reportType} (V2) - ${currentWorkspace?.name || 'workspace'}`
        )
        consoleTaskIdRef.current = consoleTaskId
      }
      
      updateTaskProgress(
        consoleTaskIdRef.current,
        status.progress,
        status.message || status.step || 'Procesando...'
      )
    } else if (status.status === 'completed') {
      if (consoleTaskIdRef.current) {
        completeTask(consoleTaskIdRef.current, 'Reporte generado exitosamente')
        consoleTaskIdRef.current = null
      }
      
      if (status.result && onReportGenerated) {
        onReportGenerated(status.result)
      }
      
      toast.success('Reporte generado exitosamente')
      setIsGenerating(false)
    } else if (status.status === 'failed') {
      if (consoleTaskIdRef.current) {
        failTask(consoleTaskIdRef.current, status.error || 'Error generando reporte')
        consoleTaskIdRef.current = null
      }
      
      toast.error(status.error || 'Error generando reporte')
      setIsGenerating(false)
    }
  }, [status, taskId, reportType, currentWorkspace, startTask, updateTaskProgress, completeTask, failTask, onReportGenerated])

  const handleGenerate = async () => {
    if (!currentWorkspace || !currentWorkspace.id) {
      toast.error('Por favor selecciona un workspace')
      return
    }

    setIsGenerating(true)
    setTaskId(null)

    try {
      const result = await reportingAPI.generateReportV2(
        currentWorkspace.id,
        reportType,
        'pdf'
      )

      setTaskId(result.task_id)
      toast.success('Generación de reporte iniciada')
    } catch (error: any) {
      console.error('Error iniciando generación de reporte V2:', error)
      toast.error(error.response?.data?.error || error.message || 'Error iniciando generación de reporte')
      setIsGenerating(false)
    }
  }

  const getStatusIcon = () => {
    if (!status) return null
    
    switch (status.status) {
      case 'pending':
        return <Loader className="w-4 h-4 animate-spin text-yellow-400" />
      case 'processing':
        return <Loader className="w-4 h-4 animate-spin text-blue-400" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-gray-900" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />
      default:
        return null
    }
  }

  const getStatusMessage = () => {
    if (!status) return 'Listo para generar'
    
    switch (status.status) {
      case 'pending':
        return 'Esperando inicio...'
      case 'processing':
        return status.message || status.step || `Procesando... ${status.progress || 0}%`
      case 'completed':
        return 'Reporte generado exitosamente'
      case 'failed':
        return status.error || 'Error generando reporte'
      default:
        return 'Estado desconocido'
    }
  }

  return (
    <div className="bg-gray-50 border border-blue-500 rounded-xl p-6">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-blue-400 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Nuevo Módulo de Reportería (V2)
        </h3>
        <p className="text-blue-600 text-sm mt-1">
          Genera reportes profesionales analizando archivos de resultados de herramientas de pentesting
        </p>
      </div>

      {/* Selector de tipo de reporte */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-600 mb-2">
          Tipo de Reporte
        </label>
        <select
          value={reportType}
          onChange={(e) => setReportType(e.target.value as any)}
          disabled={isGenerating || isPolling}
          className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 disabled:opacity-50"
        >
          <option value="technical">Técnico</option>
          <option value="executive">Ejecutivo</option>
          <option value="compliance">Cumplimiento</option>
        </select>
      </div>

      {/* Estado actual */}
      {status && (
        <div className="mb-4 p-3 bg-white rounded-xl border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon()}
            <span className="text-sm font-medium text-gray-600">
              {getStatusMessage()}
            </span>
          </div>
          
          {status.status === 'processing' && status.progress !== undefined && (
            <div className="mt-2">
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${status.progress}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1 text-right">
                {status.progress}%
              </p>
            </div>
          )}
          
          {status.status === 'failed' && status.error && (
            <div className="mt-2 flex items-start gap-2 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{status.error}</span>
            </div>
          )}
        </div>
      )}

      {/* Botón de generación */}
      <button
        type="button"
        onClick={handleGenerate}
        disabled={isGenerating || isPolling || !currentWorkspace}
        className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isGenerating || isPolling ? (
          <>
            <Loader className="w-4 h-4 animate-spin mr-2" />
            {status?.status === 'processing' ? 'Generando...' : 'Iniciando...'}
          </>
        ) : (
          <>
            <FileText className="w-4 h-4 mr-2" />
            Generar Reporte (V2)
          </>
        )}
      </button>

      {/* Botón de descarga */}
      {status?.status === 'completed' && (status.result?.result?.report_id || status.result?.result?.report_path || status.result?.report_id || status.result?.report_path) && (
        <button
          type="button"
          onClick={async () => {
            try {
              const token = localStorage.getItem('access_token')
              
              // El resultado puede estar en status.result.result (anidado) o status.result
              const resultData = status.result?.result || status.result
              
              console.log('📥 Descargando reporte:', resultData)
              
              // Usar la misma URL base que el resto del API
              const baseURL = import.meta.env.PROD ? 'http://192.168.0.11:5002' : 'http://192.168.0.11:5001'
              
              // Preferir descargar por report_id usando endpoint GET
              const downloadUrl = resultData.report_id 
                ? `${baseURL}/api/v1/reporting/download/${resultData.report_id}`
                : `${baseURL}/api/v1/reporting/download-by-path`
              
              const fetchOptions: RequestInit = {
                method: resultData.report_id ? 'GET' : 'POST',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  ...(resultData.report_id ? {} : { 'Content-Type': 'application/json' })
                },
                ...(resultData.report_id ? {} : { body: JSON.stringify({ report_path: resultData.report_path }) })
              }
              
              const response = await fetch(downloadUrl, fetchOptions)
              
              if (!response.ok) {
                throw new Error('Error descargando reporte')
              }
              
              const blob = await response.blob()
              const url = window.URL.createObjectURL(blob)
              const link = document.createElement('a')
              link.href = url
              
              // Obtener filename del header Content-Disposition o usar nombre por defecto
              const contentDisposition = response.headers.get('Content-Disposition')
              const filenameMatch = contentDisposition?.match(/filename="?(.+?)"?$/i)
              const filename = filenameMatch?.[1] || 
                               resultData.metadata?.title?.replace(/\s+/g, '_') + '.pdf' ||
                               resultData.report_path?.split('/').pop() || 
                               'reporte_tecnico.pdf'
              
              link.download = filename
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
              window.URL.revokeObjectURL(url)
              
              toast.success('Reporte descargado')
            } catch (error) {
              console.error('Error descargando:', error)
              toast.error('Error al descargar el reporte')
            }
          }}
          className="w-full mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl flex items-center justify-center transition-colors"
        >
          <Download className="w-4 h-4 mr-2" />
          Descargar Reporte PDF
        </button>
      )}

      {!currentWorkspace && (
        <p className="text-yellow-400 text-sm mt-2 text-center">
          Por favor selecciona un workspace
        </p>
      )}
    </div>
  )
}

export default ReportGeneratorV2

