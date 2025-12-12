/**
 * Reporting Mutations Hook
 * ========================
 * 
 * Hook personalizado para manejar todas las mutations de reporting.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { reportingAPI } from '../../../lib/api/reporting'
import { toast } from 'sonner'
import { useConsole } from '../../../contexts/ConsoleContext'

export const useReportingMutations = () => {
  const queryClient = useQueryClient()
  const { startTask, addLog, updateTaskProgress, completeTask, failTask } = useConsole()

  const executiveMutation = useMutation({
    mutationFn: (data: { workspaceId: number; startDate?: string; endDate?: string }) =>
      reportingAPI.generateExecutiveSummary(data.workspaceId, data.startDate, data.endDate),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Resumen ejecutivo para workspace ${data.workspaceId}`)
      addLog('info', 'reporting', `Generando resumen ejecutivo para workspace ${data.workspaceId}`, taskId, `Executive Summary - workspace: ${data.workspaceId}`)
      updateTaskProgress(taskId, 10, 'Iniciando generación de resumen ejecutivo...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      if (data.success) {
        console.log('✅ Executive summary generated successfully (raw):', data)
        console.log('✅ Executive summary generated successfully (JSON):', JSON.stringify(data, null, 2))
        console.log('🎯 Mutation onSuccess triggered')
        toast.success('Resumen ejecutivo generado exitosamente')
        queryClient.invalidateQueries({ queryKey: ['reports'] })

        if (context?.taskId) {
          updateTaskProgress(context.taskId, 100, 'Resumen ejecutivo generado exitosamente')
          addLog('success', 'reporting', 'Resumen ejecutivo generado exitosamente', context.taskId)
          completeTask(context.taskId, `Resumen ejecutivo generado para workspace ${variables.workspaceId}`)
        }
      } else {
        toast.error('Error generando resumen ejecutivo')
        if (context?.taskId) {
          failTask(context.taskId, 'Error generando resumen ejecutivo')
        }
      }
    },
    onError: (error: any, variables, context) => {
      console.error('❌ Error en mutation ejecutivo:', error)
      const errorMessage = error?.response?.data?.error || error?.message || 'Error desconocido al generar el reporte'
      toast.error(`Error: ${errorMessage}`)
      if (context?.taskId) {
        failTask(context.taskId, errorMessage)
      }
    }
  })

  const technicalMutation = useMutation({
    mutationFn: (data: { workspaceId: number; startDate?: string; endDate?: string }) =>
      reportingAPI.generateTechnicalReport(data.workspaceId, data.startDate, data.endDate),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Reporte técnico para workspace ${data.workspaceId}`)
      addLog('info', 'reporting', `Generando reporte técnico para workspace ${data.workspaceId}`, taskId, `Technical Report - workspace: ${data.workspaceId}`)
      updateTaskProgress(taskId, 10, 'Iniciando generación de reporte técnico...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      if (data.success) {
        toast.success('Reporte técnico generado exitosamente')
        queryClient.invalidateQueries({ queryKey: ['reports'] })
        if (context?.taskId) {
          updateTaskProgress(context.taskId, 100, 'Reporte técnico generado exitosamente')
          addLog('success', 'reporting', 'Reporte técnico generado exitosamente', context.taskId)
          completeTask(context.taskId, `Reporte técnico generado para workspace ${variables.workspaceId}`)
        }
      } else {
        toast.error('Error generando reporte técnico')
        if (context?.taskId) {
          failTask(context.taskId, 'Error generando reporte técnico')
        }
      }
    },
    onError: (error: any, variables, context) => {
      console.error('❌ Error en mutation técnico:', error)
      const errorMessage = error?.response?.data?.error || error?.message || 'Error desconocido al generar el reporte'
      toast.error(`Error: ${errorMessage}`)
      if (context?.taskId) {
        failTask(context.taskId, errorMessage)
      }
    }
  })

  const complianceMutation = useMutation({
    mutationFn: (data: { workspaceId: number; standard: string; startDate?: string; endDate?: string }) =>
      reportingAPI.generateComplianceReport(data.workspaceId, data.standard, data.startDate, data.endDate),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Reporte de cumplimiento ${data.standard} para workspace ${data.workspaceId}`)
      addLog('info', 'reporting', `Generando reporte de cumplimiento ${data.standard} para workspace ${data.workspaceId}`, taskId, `Compliance Report - ${data.standard}`)
      updateTaskProgress(taskId, 10, 'Iniciando generación de reporte de cumplimiento...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      if (data.success) {
        toast.success(`Reporte de cumplimiento ${data.data?.standard} generado exitosamente`)
        queryClient.invalidateQueries({ queryKey: ['reports'] })
        if (context?.taskId) {
          updateTaskProgress(context.taskId, 100, 'Reporte de cumplimiento generado exitosamente')
          addLog('success', 'reporting', `Reporte de cumplimiento ${data.data?.standard} generado exitosamente`, context.taskId)
          completeTask(context.taskId, `Reporte de cumplimiento generado para workspace ${variables.workspaceId}`)
        }
      } else {
        toast.error('Error generando reporte de cumplimiento')
        if (context?.taskId) {
          failTask(context.taskId, 'Error generando reporte de cumplimiento')
        }
      }
    },
    onError: (error: any, variables, context) => {
      console.error('❌ Error en mutation cumplimiento:', error)
      const errorMessage = error?.response?.data?.error || error?.message || 'Error desconocido al generar el reporte'
      toast.error(`Error: ${errorMessage}`)
      if (context?.taskId) {
        failTask(context.taskId, errorMessage)
      }
    }
  })

  const exportMutation = useMutation({
    mutationFn: (data: { reportData: any; format: 'json' | 'html' | 'pdf' }) =>
      reportingAPI.exportReport(data.reportData, data.format),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Exportando reporte en formato ${data.format.toUpperCase()}`)
      addLog('info', 'reporting', `Exportando reporte en formato ${data.format.toUpperCase()}`, taskId, `Report Export - format: ${data.format}`)
      updateTaskProgress(taskId, 10, 'Iniciando exportación...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      if (data.success) {
        const link = document.createElement('a')
        link.href = `data:application/octet-stream;base64,${data.content}`
        link.download = data.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        toast.success(`Reporte exportado como ${data.format.toUpperCase()}`)
        if (context?.taskId) {
          updateTaskProgress(context.taskId, 100, 'Reporte exportado exitosamente')
          addLog('success', 'reporting', `Reporte exportado como ${data.format.toUpperCase()}`, context.taskId)
          completeTask(context.taskId, `Reporte exportado en formato ${variables.format.toUpperCase()}`)
        }
      } else {
        toast.error('Error exportando reporte')
        if (context?.taskId) {
          failTask(context.taskId, 'Error exportando reporte')
        }
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error en exportación: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  return {
    executiveMutation,
    technicalMutation,
    complianceMutation,
    exportMutation
  }
}

