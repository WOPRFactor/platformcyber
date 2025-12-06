import React, { useState, useEffect } from 'react'
import { Sword, Target, Shield, Play, Zap, Users, Server, Lock, Eye, AlertCircle, FileText, Download, AlertTriangle } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { mitreAPI } from '../lib/api/mitre'
import { useAuth } from '../contexts/AuthContext'

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
  const [selectedTactic, setSelectedTactic] = useState('all')
  const [target, setTarget] = useState('')
  const [runningAttacks, setRunningAttacks] = useState<string[]>([])

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
  const { data: techniquesData } = useQuery({
    queryKey: ['mitre-techniques', selectedTactic],
    queryFn: () => mitreAPI.getTechniques(selectedTactic === 'all' ? undefined : selectedTactic),
    enabled: isAuthenticated
  })

  const { data: tacticsData } = useQuery({
    queryKey: ['mitre-tactics'],
    queryFn: () => mitreAPI.getTactics(),
    enabled: isAuthenticated
  })

  // Convertir datos de API a formato local
  const techniques: MitreTechnique[] = React.useMemo(() => {
    if (!techniquesData?.techniques) return []

    return Object.entries(techniquesData.techniques).map(([id, tech]: [string, any]) => ({
      id,
      name: tech.name,
      tactic: tech.tactic,
      description: tech.description,
      severity: tech.severity as 'low' | 'medium' | 'high' | 'critical',
      status: 'available' as const
    }))
  }, [techniquesData])

  const executeAttackMutation = useMutation({
    mutationFn: async (techniqueId: string) => {
      console.log('Ejecutando técnica MITRE:', techniqueId, 'en target:', target)

      const result = await mitreAPI.executeTechnique(techniqueId, target)

      // Marcar como ejecutándose
      setRunningAttacks(prev => [...prev, techniqueId])

      // Simular finalización después de un tiempo
      setTimeout(() => {
        setRunningAttacks(prev => prev.filter(id => id !== techniqueId))
      }, 5000)

      return result
    }
  })

  const filteredTechniques = selectedTactic === 'all'
    ? techniques
    : techniques.filter(t => t.tactic === selectedTactic)

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 border-red-400'
      case 'high': return 'text-orange-400 border-orange-400'
      case 'medium': return 'text-yellow-400 border-yellow-400'
      case 'low': return 'text-green-400 border-green-400'
      default: return 'text-gray-400 border-gray-400'
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Sword className="w-8 h-8 text-blue-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">MITRE ATT&CK Simulator</h1>
            <p className="text-gray-400">Simulador de técnicas de ataque según el framework MITRE ATT&CK</p>
          </div>
        </div>

        {/* Input para target */}
        <div className="bg-gray-700 border border-gray-600 rounded p-4">
          <label className="block text-gray-300 mb-2">Target para simulación:</label>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="192.168.1.100 o https://example.com"
            className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-400"
          />
          <p className="text-xs text-gray-500 mt-1">
            ⚠️ Solo para uso educativo y de prueba de seguridad autorizada
          </p>
        </div>
      </div>

      {/* Filtros por táctica */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">Tácticas ATT&CK</h2>

        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => setSelectedTactic('all')}
            className={`px-4 py-2 rounded text-sm font-medium ${
              selectedTactic === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
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
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
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
        {filteredTechniques.map(technique => {
          const isRunning = runningAttacks.includes(technique.id)
          const TacticIcon = getTacticIcon(technique.tactic)

          return (
            <div key={technique.id} className="bg-gray-800 border border-green-500 rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <TacticIcon className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">{technique.id}: {technique.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs border ${getSeverityColor(technique.severity)}`}>
                      {technique.severity.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-gray-400 mb-3">{technique.description}</p>

                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Táctica: {tactics.find(t => t.id === technique.tactic)?.name}</span>
                    <span>Estado: {isRunning ? 'Ejecutándose...' : 'Disponible'}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleExecuteAttack(technique.id)}
                  disabled={isRunning || executeAttackMutation.isPending}
                  className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 px-4 py-2 rounded font-medium flex items-center space-x-2 ml-4"
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
          )
        })}
      </div>

      {/* Información sobre MITRE ATT&CK */}
      <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">¿Qué es MITRE ATT&CK?</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-blue-400 font-semibold mb-2">Framework de Conocimiento</h3>
            <p className="text-gray-400 text-sm">
              MITRE ATT&CK es una base de conocimiento globalmente accesible que documenta
              tácticas y técnicas comunes de ciberataques. Ayuda a organizaciones a entender
              mejor las amenazas y mejorar sus defensas.
            </p>
          </div>

          <div>
            <h3 className="text-blue-400 font-semibold mb-2">Usos Educativos</h3>
            <p className="text-gray-400 text-sm">
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
    </div>
  )
}

export default MitreAttacks
