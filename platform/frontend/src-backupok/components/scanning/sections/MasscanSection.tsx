/**
 * MasscanSection Component
 * =========================
 * 
 * Componente para escaneos Masscan (masivo).
 */

import React, { useState, useRef } from 'react'
import { Gauge, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { scanningAPI } from '../../../lib/api/scanning'
import { commandPreviewAPI, CommandPreview } from '../../../lib/api/command-preview'
import { useWorkspace } from '../../../contexts/WorkspaceContext'
import { useTarget } from '../../../contexts/TargetContext'
import { useConsole } from '../../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import CommandPreviewModal from '../../CommandPreviewModal'

interface MasscanSectionProps {
  setActiveScanSession: (session: string | null) => void
}

const MasscanSection: React.FC<MasscanSectionProps> = ({
  setActiveScanSession
}) => {
  const { currentWorkspace } = useWorkspace()
  const { target } = useTarget()
  const { startTask, addLog, updateTask, updateTaskProgress } = useConsole()
  const queryClient = useQueryClient()
  
  // Estado para preview
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<CommandPreview | null>(null)
  const [previewToolName, setPreviewToolName] = useState('')
  const previewExecuteFnRef = useRef<(() => Promise<void>) | null>(null)

  const masscanMutation = useMutation({
    mutationFn: (ports: string = '1-65535', options?: { rate?: number; environment?: 'internal' | 'external' | 'stealth' }) => {
      if (!target?.trim() || !currentWorkspace?.id) {
        throw new Error('Target y workspace son requeridos')
      }
      const taskId = startTask('Masscan', 'scanning', undefined, target)
      addLog('info', 'scanning', `Iniciando Masscan para ${target}`, taskId, `masscan ${target} -p${ports}`)
      updateTaskProgress(taskId, 10, 'Iniciando Masscan...')
      
      return scanningAPI.masscan(target, currentWorkspace.id, ports, options).then(result => {
        if (result.scan_id) {
          updateTask(taskId, { session_id: String(result.scan_id) })
          setActiveScanSession(String(result.scan_id))
        }
        return result
      })
    },
    onSuccess: () => {
      toast.success('Masscan iniciado')
      queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.error || error?.response?.data?.details || error?.message || 'Error desconocido'
      toast.error(`Error en Masscan: ${errorMessage}`)
      console.error('Error completo de Masscan:', error)
    }
  })

  return (
    <div className="mt-4">
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Gauge className="w-5 h-5" />
            Masscan - Escaneo Masivo
          </h3>
          <p className="text-gray-500">
            Escaneo masivo de puertos a alta velocidad. Ideal para redes grandes y rangos de IP.
          </p>
        </div>
        <div className="space-y-4">
          <div className="bg-white rounded-xl p-4">
            <h4 className="text-md font-semibold text-orange-400 mb-2">Configuración</h4>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-500">Puertos</label>
                <input
                  type="text"
                  id="masscan-ports"
                  defaultValue="1-65535"
                  placeholder="1-65535 o 80,443,8080"
                  className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-600"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm text-gray-500">Rate (paquetes/seg)</label>
                  <input
                    type="number"
                    id="masscan-rate"
                    defaultValue={1000}
                    className="w-full bg-gray-50 border border-gray-200 rounded px-2 py-1 text-gray-600 text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-500">Entorno</label>
                  <select
                    id="masscan-environment"
                    className="w-full bg-gray-50 border border-gray-200 rounded px-2 py-1 text-gray-600 text-sm"
                    defaultValue="internal"
                  >
                    <option value="internal">Internal</option>
                    <option value="external">External</option>
                    <option value="stealth">Stealth</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={async () => {
              if (!target?.trim() || !currentWorkspace?.id) {
                toast.error('Target y workspace son requeridos')
                return
              }
              
              const ports = (document.getElementById('masscan-ports') as HTMLInputElement)?.value || '1-65535'
              const rate = parseInt((document.getElementById('masscan-rate') as HTMLInputElement)?.value || '1000')
              const environment = (document.getElementById('masscan-environment') as HTMLSelectElement)?.value || 'internal'
              
              try {
                const preview = await commandPreviewAPI.previewMasscan({
                  target: target.trim(),
                  workspace_id: currentWorkspace.id,
                  ports,
                  rate,
                  environment: environment as 'internal' | 'external' | 'stealth'
                })
                
                setPreviewData(preview)
                setPreviewToolName('Masscan')
                previewExecuteFnRef.current = async () => {
                  await masscanMutation.mutateAsync(ports, { rate, environment: environment as 'internal' | 'external' | 'stealth' })
                };
                setShowPreview(true)
              } catch (error: any) {
                console.error('Error obteniendo preview:', error)
                toast.error('Error al obtener preview del comando')
                // NO ejecutar el comando automáticamente - el usuario debe confirmar desde el preview
              }
            }}
            disabled={masscanMutation.isPending || !target?.trim()}
            className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl flex items-center justify-center"
          >
            {masscanMutation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Gauge className="w-4 h-4 mr-2" />
            )}
            Iniciar Masscan
          </button>
          
          <CommandPreviewModal
            isOpen={showPreview}
            onClose={() => setShowPreview(false)}
            onExecute={async () => {
              if (previewExecuteFnRef.current) {
                setShowPreview(false)
                await previewExecuteFnRef.current()
              }
            }}
            previewData={previewData}
            toolName={previewToolName}
            category="scanning"
          />
        </div>
      </div>
    </div>
  )
}

export default MasscanSection

