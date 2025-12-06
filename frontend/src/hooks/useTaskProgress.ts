import { useCallback } from 'react'
import { useConsole } from '../contexts/ConsoleContext'

export interface TaskProgressOptions {
  module: string
  target?: string
  onProgress?: (progress: number) => void
  onComplete?: () => void
  onError?: (error: string) => void
}

export const useTaskProgress = () => {
  const {
    startTask,
    updateTaskProgress,
    completeTask,
    failTask,
    cancelTask,
    addLog
  } = useConsole()

  const executeTask = useCallback(async <T>(
    taskName: string,
    options: TaskProgressOptions,
    executor: (updateProgress: (progress: number, message?: string) => void) => Promise<T>
  ): Promise<T> => {
    const { module, target, onProgress, onComplete, onError } = options

    // Iniciar tarea (esto ya abre automáticamente la consola)
    const taskId = startTask(taskName, module, undefined, target)

    const updateProgress = useCallback((progress: number, message?: string) => {
      updateTaskProgress(taskId, progress, message)
      onProgress?.(progress)
    }, [taskId, onProgress])

    try {
      // Ejecutar tarea
      const result = await executor(updateProgress)

      // Completar tarea
      completeTask(taskId, `${taskName} completada exitosamente`)
      onComplete?.()

      return result
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
      failTask(taskId, errorMessage)
      onError?.(errorMessage)
      throw error
    }
  }, [startTask, updateTaskProgress, completeTask, failTask])

  const executeCommand = useCallback(async (
    command: string,
    options: TaskProgressOptions,
    executor: (updateProgress: (progress: number, message?: string) => void) => Promise<void>
  ): Promise<void> => {
    const { module, target, onProgress, onComplete, onError } = options


    // Iniciar tarea con comando (esto ya abre automáticamente la consola)
    const taskId = startTask(`Ejecutando comando`, module, command, target)

    const updateProgress = useCallback((progress: number, message?: string) => {
      updateTaskProgress(taskId, progress, message)
      onProgress?.(progress)
    }, [taskId, onProgress])

    try {
      // Ejecutar comando
      await executor(updateProgress)

      // Completar tarea
      completeTask(taskId, `Comando ejecutado: ${command}`)
      onComplete?.()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error ejecutando comando'
      failTask(taskId, errorMessage)
      onError?.(errorMessage)
      throw error
    }
  }, [startTask, updateTaskProgress, completeTask, failTask])

  const logCommand = useCallback((module: string, command: string, taskId?: string) => {
    addLog('command', module, `Ejecutando: ${command}`, taskId, command)
  }, [addLog])

  const logInfo = useCallback((module: string, message: string, taskId?: string) => {
    addLog('info', module, message, taskId)
  }, [addLog])

  const logSuccess = useCallback((module: string, message: string, taskId?: string) => {
    addLog('success', module, message, taskId)
  }, [addLog])

  const logWarning = useCallback((module: string, message: string, taskId?: string) => {
    addLog('warning', module, message, taskId)
  }, [addLog])

  const logError = useCallback((module: string, message: string, taskId?: string) => {
    addLog('error', module, message, taskId)
  }, [addLog])

  return {
    executeTask,
    executeCommand,
    logCommand,
    logInfo,
    logSuccess,
    logWarning,
    logError
  }
}
