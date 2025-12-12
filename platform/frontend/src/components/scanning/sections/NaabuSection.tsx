/**
 * NaabuSection Component
 * ======================
 * 
 * Componente para escaneos Naabu (port discovery rápido).
 */

import React, { useState, useRef } from 'react'
import { Zap, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { scanningAPI } from '../../../lib/api/scanning'
import { commandPreviewAPI, CommandPreview } from '../../../lib/api/command-preview'
import { useWorkspace } from '../../../contexts/WorkspaceContext'
import { useTarget } from '../../../contexts/TargetContext'
import { useConsole } from '../../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import CommandPreviewModal from '../../CommandPreviewModal'

interface NaabuSectionProps {
  setActiveScanSession: (session: string | null) => void
}

const NaabuSection: React.FC<NaabuSectionProps> = ({
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

  const naabuMutation = useMutation({
    mutationFn: (options?: { top_ports?: number; rate?: number; verify?: boolean }) => {
      if (!target?.trim() || !currentWorkspace?.id) {
        throw new Error('Target y workspace son requeridos')
      }
      const taskId = startTask('Naabu', 'scanning', undefined, target)
      addLog('info', 'scanning', `Iniciando Naabu para ${target}`, taskId, `naabu -host ${target}`)
      updateTaskProgress(taskId, 10, 'Iniciando Naabu...')
      
      return scanningAPI.naabu(target, currentWorkspace.id, options).then(result => {
        if (result.scan_id) {
          updateTask(taskId, { session_id: String(result.scan_id) })
          setActiveScanSession(String(result.scan_id))
        }
        return result
      })
    },
    onSuccess: () => {
      toast.success('Naabu iniciado')
      queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })
    },
    onError: (error: Error) => {
      toast.error(`Error en Naabu: ${error.message}`)
    }
  })

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-green-400 flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Naabu - Port Discovery Rápido
          </h3>
          <p className="text-green-600">
            Descubrimiento rápido de puertos usando Naabu. Optimizado para velocidad y eficiencia.
          </p>
        </div>
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h4 className="text-md font-semibold text-purple-400 mb-2">Configuración</h4>
            <div className="grid grid-cols-3 gap-3 mb-3">
              <div>
                <label className="text-sm text-gray-400">Top Ports</label>
                <select
                  id="naabu-top-ports"
                  className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300 text-sm"
                  defaultValue=""
                >
                  <option value="">Todos</option>
                  <option value="100">Top 100</option>
                  <option value="1000">Top 1000</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400">Rate (paquetes/seg)</label>
                <input
                  type="number"
                  id="naabu-rate"
                  defaultValue={1000}
                  className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300 text-sm"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center text-sm text-gray-400">
                  <input
                    type="checkbox"
                    id="naabu-verify"
                    defaultChecked
                    className="mr-2"
                  />
                  Verificar puertos
                </label>
              </div>
            </div>
          </div>
          <button
            onClick={async () => {
              if (!target?.trim() || !currentWorkspace?.id) {
                toast.error('Target y workspace son requeridos')
                return
              }
              
              const topPorts = (document.getElementById('naabu-top-ports') as HTMLSelectElement)?.value
              const rate = parseInt((document.getElementById('naabu-rate') as HTMLInputElement)?.value || '1000')
              const verify = (document.getElementById('naabu-verify') as HTMLInputElement)?.checked
              
              try {
                const preview = await commandPreviewAPI.previewNaabu({
                  target: target.trim(),
                  workspace_id: currentWorkspace.id,
                  top_ports: topPorts ? parseInt(topPorts) : undefined,
                  rate,
                  verify
                })
                
                setPreviewData(preview)
                setPreviewToolName('Naabu')
                previewExecuteFnRef.current = async () => {
                  await naabuMutation.mutateAsync({
                    top_ports: topPorts ? parseInt(topPorts) : undefined,
                    rate,
                    verify
                  })
                };
                setShowPreview(true)
              } catch (error: any) {
                console.error('Error obteniendo preview:', error)
                toast.error('Error al obtener preview del comando')
                // NO ejecutar el comando automáticamente - el usuario debe confirmar desde el preview
              }
            }}
            disabled={naabuMutation.isPending || !target?.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center"
          >
            {naabuMutation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 mr-2" />
            )}
            Iniciar Naabu
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

export default NaabuSection

