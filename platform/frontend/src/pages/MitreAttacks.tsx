import React, { useState, useEffect } from 'react'
import { Sword, Target, Shield, Play, Zap, Users, Server, Lock, Eye, AlertCircle, FileText, Download, AlertTriangle } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { mitreAPI } from '../lib/api/mitre'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useCommandPreview } from './VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../components/CommandPreviewModal'
import { toast } from 'sonner'

interface MitreTechnique {
  id: string
  name: string
  tactic: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  status: 'available' | 'running' | 'completed'
}

interface MitreResult {
  id: string
  target: string
  technique: string
  status: 'success' | 'failed' | 'blocked'
  executed_at: string
  output: string
}

const MitreAttacks: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [selectedTactic, setSelectedTactic] = useState('all')
  const [target, setTarget] = useState('')
  const [runningAttacks, setRunningAttacks] = useState<string[]>([])
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  // Mapeo de IDs del frontend a IDs MITRE del backend
  const tacticIdMapping: Record<string, string> = {
    'reconnaissance': 'TA0043',
    'resource_development': 'TA0042',
    'initial_access': 'TA0001',
    'execution': 'TA0002',
    'persistence': 'TA0003',
    'privilege_escalation': 'TA0004',
    'defense_evasion': 'TA0005',
    'credential_access': 'TA0006',
    'discovery': 'TA0007',
    'lateral_movement': 'TA0008',
    'collection': 'TA0009',
    'command_and_control': 'TA0011',
    'exfiltration': 'TA0010',
    'impact': 'TA0040'
  }

  const tactics = [
    { id: 'reconnaissance', name: 'Reconocimiento', icon: Eye, color: 'blue' },
    { id: 'resource_development', name: 'Desarrollo de Recursos', icon: Users, color: 'green' },
    { id: 'initial_access', name: 'Acceso Inicial', icon: Target, color: 'red' },
    { id: 'execution', name: 'Ejecución', icon: Zap, color: 'yellow' },
    { id: 'persistence', name: 'Persistencia', icon: Lock, color: 'purple' },
    { id: 'privilege_escalation', name: 'Escalada de Privilegios', icon: Shield, color: 'orange' },
    { id: 'defense_evasion', name: 'Evasión de Defensas', icon: Server, color: 'gray' },
    { id: 'credential_access', name: 'Acceso a Credenciales', icon: Lock, color: 'red' },
    { id: 'discovery', name: 'Descubrimiento', icon: Eye, color: 'blue' },
    { id: 'lateral_movement', name: 'Movimiento Lateral', icon: Target, color: 'orange' },
    { id: 'collection', name: 'Recolección', icon: FileText, color: 'green' },
    { id: 'command_and_control', name: 'Command and Control', icon: Zap, color: 'purple' },
    { id: 'exfiltration', name: 'Exfiltración', icon: Download, color: 'red' },
    { id: 'impact', name: 'Impacto', icon: AlertTriangle, color: 'red' }
  ]

  // Cargar técnicas y tácticas de la API
  const { data: techniquesData, isLoading: techniquesLoading, error: techniquesError } = useQuery({
    queryKey: ['mitre-techniques', selectedTactic],
    queryFn: async () => {
      // Convertir ID del frontend a ID MITRE del backend
      const backendTacticId = selectedTactic === 'all' ? undefined : tacticIdMapping[selectedTactic]
      console.log('🔍 Filtrando técnicas:', { frontendId: selectedTactic, backendId: backendTacticId })
      const data = await mitreAPI.getTechniques(backendTacticId)
      console.log('✅ Técnicas cargadas desde API:', data)
      return data
    },
    enabled: isAuthenticated
  })

  // Log cuando cambian los datos
  React.useEffect(() => {
    if (techniquesData) {
      console.log('📊 techniquesData actualizado:', techniquesData)
    }
    if (techniquesError) {
      console.error('❌ Error cargando técnicas:', techniquesError)
    }
  }, [techniquesData, techniquesError])

  const { data: tacticsData } = useQuery({
    queryKey: ['mitre-tactics'],
    queryFn: () => mitreAPI.getTactics(),
    enabled: isAuthenticated
  })

  // Convertir datos de API a formato local
  const techniques: MitreTechnique[] = React.useMemo(() => {
    console.log('🔄 Procesando técnicas. techniquesData:', techniquesData)
    
    if (!techniquesData) {
      console.log('⚠️ No hay techniquesData')
      return []
    }

    // El frontend API client devuelve directamente el Record<string, MitreTechnique>
    // pero puede venir como { techniques: {...}, total: N } del backend
    let techniquesObj: Record<string, any> = {}
    
    if (typeof techniquesData === 'object' && 'techniques' in techniquesData) {
      techniquesObj = (techniquesData as any).techniques || {}
    } else if (typeof techniquesData === 'object') {
      techniquesObj = techniquesData as Record<string, any>
    }
    
    if (!techniquesObj || typeof techniquesObj !== 'object' || Object.keys(techniquesObj).length === 0) {
      console.log('⚠️ techniquesObj no es un objeto válido o está vacío:', techniquesObj)
      return []
    }

    const result = Object.entries(techniquesObj).map(([id, tech]: [string, any]) => ({
      id,
      name: tech.name || id,
      tactic: tech.tactic || 'unknown',
      description: tech.description || '',
      severity: (tech.severity || 'medium') as 'low' | 'medium' | 'high' | 'critical',
      status: 'available' as const
    }))
    
    console.log(`✅ ${result.length} técnicas procesadas`)
    return result
  }, [techniquesData])

  const executeAttackMutation = useMutation({
    mutationFn: async (techniqueId: string) => {
      console.log('Ejecutando técnica MITRE:', techniqueId, 'en target:', target)

      // Necesitamos un campaign_id para ejecutar. Por ahora, creamos uno temporal o usamos uno existente
      // Por simplicidad, usaremos un campaign temporal
      const campaigns = await mitreAPI.listCampaigns(currentWorkspace?.id)
      let campaignId = campaigns?.[0]?.id
      
      if (!campaignId) {
        // Crear una campaña temporal si no existe
        const newCampaign = await mitreAPI.createCampaign({
          name: `Temporary Campaign - ${techniqueId}`,
          workspace_id: currentWorkspace?.id || 1,
          techniques: [techniqueId]
        })
        campaignId = newCampaign.campaign?.id
      }

      if (!campaignId) {
        throw new Error('No se pudo obtener o crear una campaña')
      }

      const result = await mitreAPI.executeTechnique(campaignId, {
        technique_id: techniqueId,
        target: target || undefined
      })

      // Marcar como ejecutándose
      setRunningAttacks(prev => [...prev, techniqueId])

      // Simular finalización después de un tiempo
      setTimeout(() => {
        setRunningAttacks(prev => prev.filter(id => id !== techniqueId))
      }, 5000)

      return result
    }
  })

  const filteredTechniques = React.useMemo(() => {
    if (selectedTactic === 'all') {
      return techniques
    }
    
    // Convertir ID del frontend a ID MITRE del backend para filtrar
    const backendTacticId = tacticIdMapping[selectedTactic]
    console.log('🔍 Filtrando técnicas localmente:', { 
      selectedTactic, 
      backendTacticId, 
      totalTechniques: techniques.length 
    })
    
    const filtered = techniques.filter(t => {
      // Las técnicas tienen tactic como 'TA0009' (ID MITRE)
      const matches = t.tactic === backendTacticId
      if (matches) {
        console.log('✅ Técnica coincide:', t.id, t.tactic, 'con', backendTacticId)
      }
      return matches
    })
    
    console.log(`✅ ${filtered.length} técnicas filtradas de ${techniques.length} totales`)
    return filtered
  }, [techniques, selectedTactic])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 border-red-400'
      case 'high': return 'text-orange-400 border-orange-400'
      case 'medium': return 'text-yellow-400 border-yellow-400'
      case 'low': return 'text-gray-900 border-gray-200'
      default: return 'text-gray-500 border-gray-400'
    }
  }

  const getTacticIcon = (tacticId: string) => {
    const tactic = tactics.find(t => t.id === tacticId)
    return tactic ? tactic.icon : Target
  }

  const handleExecuteAttack = (techniqueId: string) => {
    if (!target.trim()) {
      alert('Por favor ingresa un target válido')
      return
    }
    executeAttackMutation.mutate(techniqueId)
  }

  const handlePreviewTechnique = async (techniqueId: string) => {
    console.log('🔍 handlePreviewTechnique llamado:', {
      techniqueId,
      target,
      workspaceId: currentWorkspace?.id,
      hasWorkspace: !!currentWorkspace
    })

    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      console.error('❌ Workspace no seleccionado')
      return
    }

    try {
      console.log('📡 Llamando a mitreAPI.previewTechnique...')
      const preview = await mitreAPI.previewTechnique(
        techniqueId,
        target || undefined,
        currentWorkspace.id
      )
      console.log('✅ Preview recibido:', preview)
      
      if (!preview || preview.error) {
        toast.error(preview?.error || 'Error obteniendo preview')
        console.error('❌ Preview tiene error:', preview)
        return
      }

      console.log('🚀 Abriendo preview modal...')
      openPreview(preview, 'MITRE ATT&CK', async () => {
        if (!target.trim()) {
          toast.error('Target es requerido para ejecutar')
          return
        }
        await executeAttackMutation.mutateAsync(techniqueId)
      })
    } catch (error: any) {
      console.error('❌ Error en handlePreviewTechnique:', error)
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Sword className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">MITRE ATT&CK Simulator</h1>
            <p className="text-gray-500">Simulador de técnicas de ataque según el framework MITRE ATT&CK</p>
          </div>
        </div>

        {/* Input para target */}
        <div className="bg-gray-700 border border-gray-200 rounded p-4">
          <label className="block text-gray-600 mb-2">Target para simulación:</label>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="192.168.1.100 o https://example.com"
            className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
          />
          <p className="text-xs text-gray-500 mt-1">
            ⚠️ Solo para uso educativo y de prueba de seguridad autorizada
          </p>
        </div>
      </div>

      {/* Filtros por táctica */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Tácticas ATT&CK</h2>

        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => setSelectedTactic('all')}
            className={`px-4 py-2 rounded text-sm font-medium ${
              selectedTactic === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-600 hover:bg-gray-600'
            }`}
          >
            Todas
          </button>
          {tactics.map(tactic => {
            const Icon = tactic.icon
            return (
              <button
                key={tactic.id}
                onClick={() => setSelectedTactic(tactic.id)}
                className={`px-4 py-2 rounded text-sm font-medium flex items-center space-x-2 ${
                  selectedTactic === tactic.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-600 hover:bg-gray-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tactic.name}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Lista de técnicas */}
      <div className="space-y-4">
        {techniquesLoading && (
          <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 text-center">
            <p className="text-gray-500">Cargando técnicas...</p>
          </div>
        )}
        {techniquesError && (
          <div className="bg-red-900 border border-red-500 rounded-xl p-6 text-center">
            <p className="text-red-400">Error cargando técnicas: {techniquesError.message}</p>
            <p className="text-red-300 text-sm mt-2">Revisa la consola para más detalles</p>
          </div>
        )}
        {!techniquesLoading && !techniquesError && filteredTechniques.length === 0 && (
          <div className="bg-gray-100 border border-gray-300 rounded-xl p-6 text-center">
            <p className="text-gray-500">No hay técnicas disponibles para la táctica seleccionada.</p>
            <p className="text-gray-500 text-sm mt-2">Total técnicas cargadas: {techniques.length}</p>
            <p className="text-gray-500 text-sm">Táctica seleccionada: {selectedTactic}</p>
            <p className="text-gray-500 text-sm mt-2">Revisa la consola para ver los datos recibidos</p>
          </div>
        )}
        {filteredTechniques.map(technique => {
          const isRunning = runningAttacks.includes(technique.id)
          const TacticIcon = getTacticIcon(technique.tactic)

          return (
            <div key={technique.id} className="bg-gray-100 border border-gray-300 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <TacticIcon className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">{technique.id}: {technique.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs border ${getSeverityColor(technique.severity)}`}>
                      {technique.severity.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-gray-500 mb-3">{technique.description}</p>

                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Táctica: {tactics.find(t => t.id === technique.tactic)?.name}</span>
                    <span>Estado: {isRunning ? 'Ejecutándose...' : 'Disponible'}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      alert(`Preview para técnica: ${technique.id}`)
                      console.log('🖱️ CLICK EN PREVIEW - técnica:', technique.id)
                      console.log('🖱️ handlePreviewTechnique existe?', typeof handlePreviewTechnique)
                      console.log('🖱️ currentWorkspace:', currentWorkspace)
                      if (typeof handlePreviewTechnique === 'function') {
                        handlePreviewTechnique(technique.id)
                      } else {
                        console.error('❌ handlePreviewTechnique no es una función!')
                        alert('Error: handlePreviewTechnique no está definida')
                      }
                    }}
                    disabled={!currentWorkspace?.id}
                    className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2 rounded font-medium flex items-center space-x-2 transition-colors"
                    title={!currentWorkspace?.id ? "Selecciona un workspace primero" : "Preview del comando"}
                    style={{ pointerEvents: 'auto', zIndex: 10 }}
                  >
                    <Eye className="w-4 h-4" />
                    <span>Preview</span>
                  </button>
                  <button
                    onClick={() => handleExecuteAttack(technique.id)}
                    disabled={isRunning || executeAttackMutation.isPending}
                    className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 px-4 py-2 rounded font-medium flex items-center space-x-2"
                  >
                    {isRunning ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <Play className="w-4 h-4" />
                    )}
                    <span>{isRunning ? 'Ejecutando...' : 'Simular Ataque'}</span>
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Información sobre MITRE ATT&CK */}
      <div className="bg-gray-100 border border-gray-300 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">¿Qué es MITRE ATT&CK?</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-blue-400 font-semibold mb-2">Framework de Conocimiento</h3>
            <p className="text-gray-500 text-sm">
              MITRE ATT&CK es una base de conocimiento globalmente accesible que documenta
              tácticas y técnicas comunes de ciberataques. Ayuda a organizaciones a entender
              mejor las amenazas y mejorar sus defensas.
            </p>
          </div>

          <div>
            <h3 className="text-blue-400 font-semibold mb-2">Usos Educativos</h3>
            <p className="text-gray-500 text-sm">
              Este simulador permite practicar técnicas de ataque en entornos controlados
              para fines educativos y de investigación de seguridad. Nunca debe usarse
              en sistemas reales sin autorización expresa.
            </p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-yellow-900 border border-yellow-600 rounded">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-yellow-400 font-semibold">Advertencia Legal</h4>
              <p className="text-yellow-200 text-sm mt-1">
                El uso de estas técnicas sin autorización constituye un delito. Este simulador
                es exclusivamente para fines educativos y de investigación de seguridad autorizada.
              </p>
            </div>
          </div>
        </div>
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

export default MitreAttacks
