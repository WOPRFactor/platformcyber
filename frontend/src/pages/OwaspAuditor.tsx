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
  const [currentAudit, setCurrentAudit] = useState<OwaspResult | null>(null)
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  // Simular datos de ejemplo
  const mockResults: OwaspResult = {
    id: 'audit-001',
    target: '192.168.1.100',
    status: 'completed',
    progress: 100,
    vulnerabilities: {
      a01_access_control: 3,
      a02_crypto_failures: 1,
      a03_injection: 2,
      a04_insecure_design: 0,
      a05_misconfig: 4,
      a06_vuln_components: 1,
      a07_auth_failures: 2,
      a08_integrity_failures: 0,
      a09_logging_failures: 1,
      a10_ssrf: 1
    },
    started_at: '2025-11-15T01:30:00Z',
    completed_at: '2025-11-15T01:45:00Z'
  }

  const startAuditMutation = useMutation({
    mutationFn: async (targetUrl: string) => {
      const result = await owaspAPI.startAudit(targetUrl)
      setCurrentAudit({
        id: result.audit.id,
        target: targetUrl,
        status: 'running',
        progress: 0,
        vulnerabilities: {
          a01_access_control: 0,
          a02_crypto_failures: 0,
          a03_injection: 0,
          a04_insecure_design: 0,
          a05_misconfig: 0,
          a06_vuln_components: 0,
          a07_auth_failures: 0,
          a08_integrity_failures: 0,
          a09_logging_failures: 0,
          a10_ssrf: 0
        },
        started_at: result.audit.started_at
      })

      // Simular progreso mientras la auditoría corre
      const progressInterval = setInterval(() => {
        setCurrentAudit(prev => {
          if (!prev || prev.status === 'completed') {
            clearInterval(progressInterval)
            return prev
          }

          const newProgress = Math.min(prev.progress + 10, 90)
          return { ...prev, progress: newProgress }
        })
      }, 2000)

      // Verificar estado final después de un tiempo
      setTimeout(async () => {
        try {
          const statusResult = await owaspAPI.getAuditStatus(result.audit.id)
          setCurrentAudit(prev => prev ? {
            ...prev,
            ...statusResult.audit,
            status: 'completed',
            progress: 100
          } : null)
        } catch (error) {
          console.error('Error obteniendo estado final:', error)
          setCurrentAudit(prev => prev ? { ...prev, status: 'failed' } : null)
        }
      }, 10000)

      return result
    }
  })

  // Cargar categorías OWASP
  const { data: categoriesData } = useQuery({
    queryKey: ['owasp-categories'],
    queryFn: () => owaspAPI.getCategories(),
    enabled: isAuthenticated
  })

  const handleStartAudit = () => {
    if (!target.trim()) return
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
    if (count === 0) return 'text-green-400'
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
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="w-8 h-8 text-red-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">OWASP Top 10 Auditor</h1>
            <p className="text-gray-400">Auditoría automática de vulnerabilidades según OWASP Top 10</p>
          </div>
        </div>

        {/* Input para target */}
        <div className="flex space-x-4">
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="https://example.com o 192.168.1.100"
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-red-400"
          />
          <button
            onClick={handleAuditWithPreview}
            disabled={startAuditMutation.isPending || !target.trim()}
            className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 px-6 py-2 rounded font-medium flex items-center space-x-2"
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
            disabled={!target.trim()}
            className="bg-gray-600 hover:bg-gray-700 px-6 py-2 rounded font-medium flex items-center space-x-2"
          >
            <Eye className="w-4 h-4" />
            <span>Preview</span>
          </button>
        </div>
      </div>

      {/* Estado de auditoría actual */}
      {currentAudit && (
        <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Auditoría en Progreso</h2>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-300">Target: {currentAudit.target}</span>
              <span className={`px-2 py-1 rounded text-sm ${
                currentAudit.status === 'running' ? 'bg-yellow-600' :
                currentAudit.status === 'completed' ? 'bg-green-600' : 'bg-red-600'
              }`}>
                {currentAudit.status === 'running' ? 'Ejecutándose' :
                 currentAudit.status === 'completed' ? 'Completada' : 'Fallida'}
              </span>
            </div>

            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-red-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${currentAudit.progress}%` }}
              ></div>
            </div>

            <div className="text-center text-gray-400">
              {currentAudit.progress}% completado
            </div>
          </div>
        </div>
      )}

      {/* Resultados de ejemplo */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
          <FileText className="w-5 h-5" />
          <span>Últimos Resultados</span>
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(mockResults.vulnerabilities).map(([category, count]) => (
            <div key={category} className="bg-gray-700 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                {getRiskIcon(count)}
                <span className="text-sm text-gray-300 uppercase">{category}</span>
              </div>
              <div className={`text-2xl font-bold ${getRiskColor(count)}`}>
                {count}
              </div>
              <div className="text-xs text-gray-500">vulnerabilidades</div>
            </div>
          ))}
        </div>

        <div className="mt-6 text-center">
          <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm">
            Ver Reporte Completo
          </button>
        </div>
      </div>

      {/* Información sobre OWASP Top 10 */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">OWASP Top 10 - Categorías</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {categoriesData?.categories && Object.entries(categoriesData.categories).map(([key, category]: [string, any]) => (
            <div key={key}>
              <h3 className={`font-semibold mb-2 ${
                category.severity === 'critical' ? 'text-red-400' :
                category.severity === 'high' ? 'text-orange-400' :
                category.severity === 'medium' ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {key.toUpperCase()} - {category.name}
              </h3>
              <p className="text-gray-400">{category.description}</p>
            </div>
          ))}
        </div>

        {!categoriesData?.categories && (
          <div className="text-center text-gray-500 py-8">
            Cargando categorías OWASP...
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
