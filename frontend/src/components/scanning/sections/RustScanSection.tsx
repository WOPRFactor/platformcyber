/**
 * RustScanSection Component
 * =========================
 * 
 * Componente para escaneos RustScan (ultra-rápido).
 */

import React, { useState, useRef } from 'react'
import { Rocket, Loader2 } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { scanningAPI } from '../../../lib/api/scanning'
import { commandPreviewAPI, CommandPreview } from '../../../lib/api/command-preview'
import { useWorkspace } from '../../../contexts/WorkspaceContext'
import { useTarget } from '../../../contexts/TargetContext'
import { useConsole } from '../../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import CommandPreviewModal from '../../CommandPreviewModal'

interface RustScanSectionProps {
  setActiveScanSession: (session: string | null) => void
}

const RustScanSection: React.FC<RustScanSectionProps> = ({
  setActiveScanSession
}) => {
  const { currentWorkspace } = useWorkspace()
  const { target } = useTarget()
  const { startTask, addLog, updateTask, updateTaskProgress, failTask } = useConsole()
  const queryClient = useQueryClient()
  
  // Estado para preview
  const [showPreview, setShowPreview] = useState(false)
  const [previewData, setPreviewData] = useState<CommandPreview | null>(null)
  const [previewToolName, setPreviewToolName] = useState('')
  const previewExecuteFnRef = useRef<(() => Promise<void>) | null>(null)

  const rustscanMutation = useMutation({
    mutationFn: async (options?: { batch_size?: number; timeout?: number; ulimit?: number }) => {
      if (!target?.trim() || !currentWorkspace?.id) {
        throw new Error('Target y workspace son requeridos')
      }
      const taskId = startTask('RustScan', 'scanning', undefined, target)
      addLog('info', 'scanning', `Iniciando RustScan para ${target}`, taskId, `rustscan -a ${target}`)
      updateTaskProgress(taskId, 10, 'Iniciando RustScan...')
      
      try {
        const result = await scanningAPI.rustscan(target, currentWorkspace.id, options)
        if (result.scan_id) {
          updateTask(taskId, { session_id: String(result.scan_id) })
          setActiveScanSession(String(result.scan_id))
        }
        return result
      } catch (error: any) {
        // Extraer mensaje de error del backend
        const errorMessage = error?.response?.data?.error || 
                            error?.response?.data?.details || 
                            error?.message || 
                            'Error desconocido al iniciar RustScan'
        
        // Marcar la tarea como fallida con el mensaje de error
        failTask(taskId, errorMessage)
        
        // Re-lanzar el error original para que onError lo maneje
        throw error
      }
    },
    onSuccess: () => {
      toast.success('RustScan iniciado')
      queryClient.invalidateQueries({ queryKey: ['scan-sessions'] })
    },
    onError: (error: any) => {
      // Log detallado para debugging
      console.error('[RustScan] Error completo:', {
        error,
        response: error?.response,
        data: error?.response?.data,
        message: error?.message
      })
      
      // Extraer mensaje de error del backend
      const errorMessage = error?.response?.data?.error || 
                          error?.response?.data?.details || 
                          error?.message || 
                          'Error desconocido al iniciar RustScan'
      
      console.error('[RustScan] Mensaje de error extraído:', errorMessage)
      
      toast.error(`Error en RustScan: ${errorMessage}`)
      
      // Si hay un taskId en el contexto, marcar la tarea como fallida
      // (el taskId se crea en mutationFn pero no está disponible aquí directamente)
      // Se manejará en el monitoreo del progreso
    }
  })

  return (
    <div className="mt-4">
      <div className="bg-gray-900 border border-green-500 rounded-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-green-400 flex items-center gap-2">
            <Rocket className="w-5 h-5" />
            RustScan - Escaneo Ultra-Rápido
          </h3>
          <p className="text-green-600">
            Escaneo de puertos extremadamente rápido usando RustScan. Ideal para escaneos masivos de puertos.
          </p>
        </div>
        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h4 className="text-md font-semibold text-cyan-400 mb-2">Opciones Avanzadas</h4>
            <div className="grid grid-cols-3 gap-3 mb-3">
              <div>
                <label className="text-sm text-gray-400">Batch Size</label>
                <input
                  type="number"
                  id="rustscan-batch"
                  defaultValue={4000}
                  className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300 text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400">Timeout (ms)</label>
                <input
                  type="number"
                  id="rustscan-timeout"
                  defaultValue={1500}
                  className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300 text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-gray-400">Ulimit</label>
                <input
                  type="number"
                  id="rustscan-ulimit"
                  defaultValue={5000}
                  className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300 text-sm"
                />
              </div>
            </div>
          </div>
          <button
            onClick={async () => {
              if (!target?.trim() || !currentWorkspace?.id) {
                toast.error('Target y workspace son requeridos')
                return
              }
              
              const batchSize = parseInt((document.getElementById('rustscan-batch') as HTMLInputElement)?.value || '4000')
              const timeout = parseInt((document.getElementById('rustscan-timeout') as HTMLInputElement)?.value || '1500')
              const ulimit = parseInt((document.getElementById('rustscan-ulimit') as HTMLInputElement)?.value || '5000')
              
              try {
                const preview = await commandPreviewAPI.previewRustscan({
                  target: target.trim(),
                  workspace_id: currentWorkspace.id,
                  batch_size: batchSize,
                  timeout,
                  ulimit
                })
                
                setPreviewData(preview)
                setPreviewToolName('RustScan')
                previewExecuteFnRef.current = async () => {
                  await rustscanMutation.mutateAsync({ batch_size: batchSize, timeout, ulimit })
                };
                setShowPreview(true)
              } catch (error: any) {
                console.error('Error obteniendo preview:', error)
                toast.error('Error al obtener preview del comando')
                // NO ejecutar el comando automáticamente - el usuario debe confirmar desde el preview
              }
            }}
            disabled={rustscanMutation.isPending || !target?.trim()}
            className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-cyan-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center"
          >
            {rustscanMutation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Rocket className="w-4 h-4 mr-2" />
            )}
            Iniciar RustScan
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

export default RustScanSection

