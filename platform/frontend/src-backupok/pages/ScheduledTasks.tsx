import React, { useState, useEffect } from 'react'
import {
  Clock, Play, Pause, Plus, Trash2, Settings, CheckCircle,
  AlertTriangle, Calendar, Zap, Database, FileText, Shield, Eye
} from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { schedulerAPI } from '../lib/api/scheduler'
import LoadingSpinner from '../components/LoadingSpinner'
import { TextInput, Select, FormField } from '../components/FormField'
import { useFormValidation } from '../hooks/useFormValidation'
import { validationSchemas } from '../utils/validationSchemas'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useCommandPreview } from './VulnerabilityAssessment/hooks/useCommandPreview'
import CommandPreviewModal from '../components/CommandPreviewModal'
import { toast } from 'sonner'

import type { ScheduledScan, CreateScheduledScanData } from '../lib/api/scheduler/types'

interface ScheduledTask extends ScheduledScan {
  // Alias para compatibilidad con UI existente
}

const ScheduledTasks: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const queryClient = useQueryClient()
  const commandPreview = useCommandPreview()
  const { showPreview, previewData, previewToolName, closePreview, executePreview, openPreview } = commandPreview

  // Form state
  const [formData, setFormData] = useState<CreateScheduledScanData>({
    scan_id: '',
    scan_type: 'nmap',
    target: '',
    schedule: 'every day',
    options: {}
  })

  // Validation
  const { errors, isValid, validateForm, validateSingleField } = useFormValidation(
    validationSchemas.scheduledTask
  )

  // Queries
  const { data: tasksData, isLoading: tasksLoading, refetch: refetchTasks } = useQuery({
    queryKey: ['scheduled-scans'],
    queryFn: () => schedulerAPI.listScheduledScans(),
    enabled: isAuthenticated,
    refetchInterval: 10000 // Actualizar cada 10 segundos
  })

  // Mutations
  const createTaskMutation = useMutation({
    mutationFn: (scanData: CreateScheduledScanData) => schedulerAPI.createScheduledScan(scanData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduled-scans'] })
      setShowCreateForm(false)
      resetForm()
    }
  })

  const deleteTaskMutation = useMutation({
    mutationFn: (scanId: string) => schedulerAPI.cancelScheduledScan(scanId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduled-scans'] })
    }
  })

  const resetForm = () => {
    setFormData({
      scan_id: '',
      scan_type: 'nmap',
      target: '',
      schedule: 'every day',
      options: {}
    })
    setSelectedTemplate('')
  }


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm(formData)) {
      return
    }

    createTaskMutation.mutate(formData)
  }

  const handlePreview = async () => {
    if (!validateForm(formData)) {
      return
    }
    if (!currentWorkspace?.id) {
      toast.error('Workspace no seleccionado')
      return
    }

    try {
      const preview = await schedulerAPI.previewScheduledScan({
        scan_type: formData.scan_type,
        target: formData.target,
        schedule: formData.schedule,
        options: { ...formData.options, workspace_id: currentWorkspace.id }
      })
      openPreview(preview, 'Scheduled Tasks', async () => {
        await createTaskMutation.mutateAsync(formData)
      })
    } catch (error: any) {
      toast.error(`Error obteniendo preview: ${error.message}`)
    }
  }

  const getFunctionIcon = (scanType: string) => {
    switch (scanType) {
      case 'nmap': return Shield
      case 'nuclei': return Zap
      case 'nikto': return Database
      case 'sqlmap': return Shield
      case 'custom_script': return FileText
      case 'cleanup_old_data': return Database
      case 'database_backup': return Database
      default: return Clock
    }
  }

  const getStatusColor = (task: ScheduledTask) => {
    if (task.status === 'cancelled') return 'text-red-400'
    if (task.status === 'completed') return 'text-gray-500'
    if (!task.next_run) return 'text-yellow-400'
    const nextRun = new Date(task.next_run)
    const now = new Date()
    const diffMinutes = (nextRun.getTime() - now.getTime()) / (1000 * 60)
    
    if (diffMinutes < 0) return 'text-red-400' // Atrasada
    if (diffMinutes < 60) return 'text-yellow-400' // Próxima
    return 'text-gray-900' // Normal
  }

  const formatDateTime = (dateString: string | null) => {
    if (!dateString) return 'Nunca'
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 text-gray-900 flex items-center">
            <Clock className="w-8 h-8 mr-3" />
            Tareas Programadas
          </h1>
          <p className="text-gray-500 mt-2">
            Automatiza escaneos, reportes y mantenimiento del sistema
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Estado del Scheduler */}
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-sm text-gray-500">
              Scheduler: Activo
            </span>
            <span className="text-sm text-gray-500">
              ({tasksData?.length || 0} tareas)
            </span>
          </div>

          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
          >
            <Plus size={16} />
            <span>Nueva Tarea</span>
          </button>
        </div>
      </div>

      {/* Lista de Tareas */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          Tareas Activas
        </h2>

        {tasksLoading ? (
          <LoadingSpinner message="Cargando tareas programadas..." />
        ) : tasksData && tasksData.length > 0 ? (
          <div className="space-y-4">
            {tasksData.map((task: ScheduledTask) => {
              const FunctionIcon = getFunctionIcon(task.scan_type)
              return (
                <div key={task.scan_id} className="flex items-center justify-between p-4 bg-white/50 rounded-xl border border-gray-200/20">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-xl ${task.status === 'active' ? 'bg-red-600/10' : 'bg-red-500/10'}`}>
                      <FunctionIcon className={`w-5 h-5 ${task.status === 'active' ? 'text-gray-900' : 'text-red-400'}`} />
                    </div>

                    <div>
                      <h3 className="text-white font-medium">{task.scan_type} - {task.target}</h3>
                      <p className="text-gray-500 text-sm">
                        ID: {task.scan_id} • Horario: {task.schedule}
                      </p>
                      <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                        <span>Próxima ejecución: {formatDateTime(task.next_run)}</span>
                        <span>Estado: {task.status}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        if (window.confirm(`¿Cancelar el escaneo programado "${task.scan_id}"?`)) {
                          deleteTaskMutation.mutate(task.scan_id)
                        }
                      }}
                      disabled={deleteTaskMutation.isPending}
                      className="p-2 text-red-400 hover:bg-red-500/10 rounded-xl transition-colors"
                      title="Eliminar tarea"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Clock size={48} className="mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No hay tareas programadas</p>
            <p className="text-sm">Crea tu primera tarea automática</p>
          </div>
        )}
      </div>

      {/* Plantillas Disponibles */}
      {/* Modal de Creación de Tarea */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <Plus className="w-5 h-5 mr-2" />
                Crear Nueva Tarea Programada
              </h2>
              <button
                onClick={() => setShowCreateForm(false)}
                className="text-gray-500 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <TextInput
                label="Nombre de la Tarea"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Escaneo Nmap Diario"
                required
                helperText="Nombre descriptivo para la tarea programada"
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Select
                  label="Tipo de Escaneo"
                  value={formData.scan_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, scan_type: e.target.value }))}
                  options={[
                    { value: 'nmap', label: 'Nmap' },
                    { value: 'nuclei', label: 'Nuclei' },
                    { value: 'nikto', label: 'Nikto' },
                    { value: 'sqlmap', label: 'SQLMap' }
                  ]}
                  required
                />

                <TextInput
                  label="Objetivo (Target)"
                  value={formData.target}
                  onChange={(e) => setFormData(prev => ({ ...prev, target: e.target.value }))}
                  placeholder="example.com o 192.168.1.1"
                  required
                  helperText="Dominio o dirección IP a escanear"
                />
              </div>

              <Select
                label="Frecuencia de Ejecución"
                value={formData.schedule}
                onChange={(e) => setFormData(prev => ({ ...prev, schedule: e.target.value }))}
                options={[
                  { value: 'every hour', label: 'Cada hora' },
                  { value: 'every 6h', label: 'Cada 6 horas' },
                  { value: 'every 12h', label: 'Cada 12 horas' },
                  { value: 'every day', label: 'Diario' },
                  { value: 'every week', label: 'Semanal' }
                ]}
                required
                helperText="Define con qué frecuencia se ejecutará el escaneo"
              />

              <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false)
                    resetForm()
                  }}
                  className="px-4 py-2 text-gray-500 hover:text-white transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handlePreview}
                  disabled={!isValid}
                  className="px-6 py-2 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 text-white rounded-xl font-medium transition-colors flex items-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>Preview</span>
                </button>
                <button
                  type="submit"
                  disabled={!isValid || createTaskMutation.isPending}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-xl font-medium transition-colors"
                >
                  {createTaskMutation.isPending ? 'Creando...' : 'Crear Tarea'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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

export default ScheduledTasks
