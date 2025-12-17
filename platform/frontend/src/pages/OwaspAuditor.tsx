import React, { useState, useEffect } from 'react'
import { Shield, Play, Pause, RotateCcw, FileText, AlertTriangle, CheckCircle, Clock, Target, Eye } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { owaspAPI } from '../lib/api/owasp'
import { systemAPI } from '../lib/api/system'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useCommandPreview } from './VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../components/CommandPreviewModal'
import { toast } from 'sonner'

interface OwaspResult {
  id: string
  target: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  vulnerabilities: {
    a01_access_control: number
    a02_crypto_failures: number
    a03_injection: number
    a04_insecure_design: number
    a05_misconfig: number
    a06_vuln_components: number
    a07_auth_failures: number
    a08_integrity_failures: number
    a09_logging_failures: number
    a10_ssrf: number
  }
  started_at: string
  completed_at?: string
}

const OwaspAuditor: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [target, setTarget] = useState('')
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  const startAuditMutation = useMutation({
    mutationFn: async (targetUrl: string) => {
      if (!currentWorkspace?.id) {
        throw new Error('Workspace no seleccionado')
      }

      console.log('🚀 Iniciando auditoría OWASP:', { target: targetUrl, workspaceId: currentWorkspace.id })
      
      const result = await owaspAPI.createAudit({
        target: targetUrl,
        workspace_id: currentWorkspace.id
      })

      console.log('✅ Auditoría creada:', result)

      if (!result.success || !result.audit) {
        throw new Error(result.error || 'Error al crear la auditoría')
      }

      // Limpiar el input después de crear la auditoría
      setTarget('')

      return result
    },
    onError: (error: any) => {
      console.error('❌ Error en startAuditMutation:', error)
      toast.error(`Error al iniciar auditoría: ${error.message}`)
    },
    onSuccess: (data) => {
      console.log('✅ Auditoría iniciada exitosamente:', data)
      toast.success('Auditoría OWASP iniciada correctamente')
      refetchAudits() // Refrescar lista de auditorías
    }
  })

  // Cargar categorías OWASP
  const { data: categoriesData, isLoading: categoriesLoading } = useQuery({
    queryKey: ['owasp-categories'],
    queryFn: async () => {
      const data = await owaspAPI.getCategories()
      console.log('✅ Categorías OWASP cargadas:', data)
      return data
    },
    enabled: isAuthenticated,
    onError: (error) => {
      console.error('❌ Error cargando categorías OWASP:', error)
    }
  })

  // Cargar auditorías existentes
  const { data: auditsData, isLoading: auditsLoading, refetch: refetchAudits } = useQuery({
    queryKey: ['owasp-audits', currentWorkspace?.id],
    queryFn: () => owaspAPI.listAudits({ workspace_id: currentWorkspace?.id }),
    enabled: isAuthenticated && !!currentWorkspace?.id,
    refetchInterval: 5000, // Actualizar cada 5 segundos
    onError: (error) => {
      console.error('❌ Error cargando auditorías:', error)
    }
  })

  const handleStartAudit = () => {
    if (!target.trim()) {
      toast.error('Target es requerido')
      return
    }
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }
    console.log('🚀 Iniciando auditoría directamente (sin preview)')
    startAuditMutation.mutate(target)
  }

  const handleAuditWithPreview = async () => {
    if (!target.trim()) {
      toast.error('Target es requerido')
      return
    }
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }

    try {
      const preview = await owaspAPI.previewAudit({
        target,
        workspace_id: currentWorkspace.id
      })
      openPreview(preview, 'OWASP Auditor', async () => {
        await startAuditMutation.mutateAsync(target)
      })
    } catch (error: any) {
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  const getRiskColor = (count: number) => {
    if (count === 0) return 'text-gray-900'
    if (count <= 2) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getRiskIcon = (count: number) => {
    if (count === 0) return <CheckCircle className="w-4 h-4" />
    if (count <= 2) return <AlertTriangle className="w-4 h-4" />
    return <Target className="w-4 h-4" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="w-8 h-8 text-red-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">OWASP Top 10 Auditor</h1>
            <p className="text-gray-500">Auditoría automática de vulnerabilidades según OWASP Top 10</p>
          </div>
        </div>

        {/* Input para target */}
        <div className="flex space-x-4">
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="https://example.com o 192.168.1.100"
            className="flex-1 bg-gray-700 border border-gray-200 rounded px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-red-400"
          />
          <button
            onClick={handleStartAudit}
            disabled={startAuditMutation.isPending || !target.trim() || !currentWorkspace?.id}
            className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:opacity-50 px-6 py-2 rounded font-medium flex items-center space-x-2"
          >
            {startAuditMutation.isPending ? (
              <RotateCcw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>Iniciar Auditoría</span>
          </button>
          <button
            onClick={handleAuditWithPreview}
            disabled={!target.trim() || !currentWorkspace?.id}
            className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 disabled:opacity-50 px-6 py-2 rounded font-medium flex items-center space-x-2"
            title="Ver preview del comando antes de ejecutar"
          >
            <Eye className="w-4 h-4" />
            <span>Preview</span>
          </button>
        </div>
      </div>


      {/* Lista de Auditorías */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
          <FileText className="w-5 h-5" />
          <span>Auditorías OWASP</span>
          {auditsLoading && <span className="text-sm text-gray-500">(Cargando...)</span>}
        </h2>

        {auditsLoading ? (
          <div className="text-center py-8 text-gray-500">
            Cargando auditorías...
          </div>
        ) : auditsData && auditsData.length > 0 ? (
          <div className="space-y-4">
            {auditsData.map((audit: any) => {
              const vulnerabilities = audit.vulnerabilities || {}
              const totalVulns = Object.values(vulnerabilities).reduce((sum: number, count: any) => sum + (count || 0), 0)
              
              return (
                <div key={audit.id} className="bg-gray-700 rounded-xl p-4 border border-gray-200">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-white font-semibold">{audit.target}</h3>
                      <p className="text-gray-500 text-sm">
                        ID: {audit.id} • {new Date(audit.started_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 rounded text-sm ${
                        audit.status === 'completed' ? 'bg-red-600' :
                        audit.status === 'running' ? 'bg-yellow-600' :
                        audit.status === 'failed' ? 'bg-red-600' : 'bg-gray-600'
                      }`}>
                        {audit.status}
                      </span>
                      {audit.status === 'running' && (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      )}
                    </div>
                  </div>
                  
                  {audit.status === 'running' && (
                    <div className="mb-3">
                      <div className="w-full bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-yellow-600 h-2 rounded-full transition-all"
                          style={{ width: `${audit.progress || 0}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{audit.progress || 0}% completado</p>
                    </div>
                  )}

                  {totalVulns > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mt-3">
                      {Object.entries(vulnerabilities).slice(0, 5).map(([category, count]: [string, any]) => (
                        count > 0 && (
                          <div key={category} className="bg-gray-600 rounded p-2 text-center">
                            <div className={`text-lg font-bold ${getRiskColor(count)}`}>
                              {count}
                            </div>
                            <div className="text-xs text-gray-500 uppercase">{category.replace('a0', 'A').replace('_', ' ')}</div>
                          </div>
                        )
                      ))}
                    </div>
                  )}

                  {audit.status === 'completed' && totalVulns === 0 && (
                    <p className="text-gray-900 text-sm">✅ No se encontraron vulnerabilidades</p>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No hay auditorías realizadas aún.</p>
            <p className="text-sm mt-2">Inicia una auditoría usando el formulario de arriba.</p>
          </div>
        )}
      </div>

      {/* Información sobre OWASP Top 10 */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">OWASP Top 10 - Categorías</h2>

        {categoriesLoading ? (
          <div className="text-center text-gray-500 py-8">
            Cargando categorías OWASP...
          </div>
        ) : categoriesData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {Object.entries(categoriesData).map(([key, category]: [string, any]) => (
              <div key={key} className="border border-gray-200 rounded p-3">
                <h3 className="font-semibold mb-2 text-red-400">
                  {key.toUpperCase()} - {category.name}
                </h3>
                <p className="text-gray-500">{category.description}</p>
                {category.tests && category.tests.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500">Tests: {category.tests.join(', ')}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-red-500 py-8">
            Error cargando categorías OWASP. Revisa la consola.
          </div>
        )}
      </div>

      <CommandPreviewModal
        isOpen={showPreview}
        onClose={closePreview}
        previewData={previewData}
        category="Herramientas Auxiliares"
        toolName={previewToolName}
        onExecute={async () => {
          await executePreview()
        }}
      />
    </div>
  )
}

export default OwaspAuditor
