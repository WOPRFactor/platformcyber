import { reconnaissanceAPI } from '../../../lib/api/reconnaissance'
import { useConsole } from '../../../contexts/ConsoleContext'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'

export const useReconnaissanceScan = () => {
  const { startTask, addLog, updateTaskProgress, failTask, completeTask } = useConsole()
  const queryClient = useQueryClient()

  const startReconScan = async (
    toolName: string,
    apiCall: () => Promise<any>,
    command?: string,
    target?: string
  ) => {
    if (!target?.trim()) {
      toast.error('Por favor ingrese un target válido')
      return
    }

    const taskId = startTask(toolName, 'reconnaissance', undefined, target)
    addLog('info', 'reconnaissance', `Iniciando ${toolName} para ${target}`, taskId, command || `${toolName} ${target}`)
    updateTaskProgress(taskId, 10, `Iniciando ${toolName}...`)

    try {
      const result = await apiCall()
      updateTaskProgress(taskId, 50, `${toolName} ejecutándose...`)
      
      const scanIds = result.scan_ids || (result.scan_id ? [result.scan_id] : [])
      
      if (scanIds.length > 0) {
        let monitoringActive = true
        
        const checkProgress = async () => {
          if (!monitoringActive) return
          
          try {
            const statusPromises = scanIds.map(scanId => 
              reconnaissanceAPI.getScanStatus(scanId).catch(() => null)
            )
            
            const statuses = await Promise.all(statusPromises)
            const validStatuses = statuses.filter(s => s !== null)
            
            if (validStatuses.length === 0) {
              setTimeout(checkProgress, 5000)
              return
            }
            
            const totalProgress = validStatuses.reduce((sum, s) => sum + (s.progress || 0), 0)
            const avgProgress = Math.round(totalProgress / validStatuses.length)
            const allCompleted = validStatuses.every(s => s.status === 'completed')
            const anyFailed = validStatuses.some(s => s.status === 'failed')
            const anyRunning = validStatuses.some(s => s.status === 'running')
            
            if (avgProgress !== undefined && avgProgress !== null) {
              const progressMessage = allCompleted
                ? `${toolName} completado (${avgProgress}%)`
                : anyFailed && !anyRunning
                ? `${toolName} finalizado con errores (${avgProgress}%)`
                : anyRunning
                ? `${toolName} ejecutándose... (${avgProgress}%)`
                : `${toolName} en progreso... (${avgProgress}%)`
              
              updateTaskProgress(taskId, avgProgress, progressMessage)
            }
            
            if (allCompleted) {
              monitoringActive = false
              updateTaskProgress(taskId, 100, `${toolName} completado`)
              completeTask(taskId, `${toolName} completado exitosamente`)
              toast.success(`${toolName} completado`)
            } else if (anyFailed && !anyRunning) {
              monitoringActive = false
              const failedScans = validStatuses.filter(s => s.status === 'failed')
              const errorMessages = failedScans.map(s => s.error || 'Error desconocido').join(', ')
              updateTaskProgress(taskId, avgProgress, `${toolName} finalizado con errores`)
              failTask(taskId, errorMessages || 'Algunos scans fallaron')
              toast.error(`${toolName} finalizado con errores`)
            } else if (anyRunning) {
              setTimeout(checkProgress, 5000)
            } else {
              setTimeout(checkProgress, 5000)
            }
          } catch (error) {
            console.error(`Error checking ${toolName} progress:`, error)
            setTimeout(checkProgress, 5000)
          }
        }
        
        setTimeout(checkProgress, 1000)
      }

      toast.success(`${toolName} iniciado correctamente`)
      queryClient.invalidateQueries({ queryKey: ['recon-sessions'] })
      
      return result
    } catch (error: any) {
      const errorMessage = error?.response?.data?.error || error?.message || 'Error desconocido'
      failTask(taskId, errorMessage)
      toast.error(`Error en ${toolName}: ${errorMessage}`)
      throw error
    }
  }

  return { startReconScan }
}

