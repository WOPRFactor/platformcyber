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
    mutationFn: (data: { target: string; startDate?: string; endDate?: string }) =>
      reportingAPI.generateExecutiveSummary(data.target, data.startDate, data.endDate),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Resumen ejecutivo para ${data.target}`)
      addLog('info', 'reporting', `Generando resumen ejecutivo para ${data.target}`, taskId, `Executive Summary - target: ${data.target}`)
      updateTaskProgress(taskId, 10, 'Iniciando generación de resumen ejecutivo...')
      return { taskId }
    },
    onSuccess: (data, variables, context) => {
      if (data.success) {
        toast.success('Resumen ejecutivo generado exitosamente')
        queryClient.invalidateQueries({ queryKey: ['reports'] })
        if (context?.taskId) {
          updateTaskProgress(context.taskId, 100, 'Resumen ejecutivo generado exitosamente')
          addLog('success', 'reporting', 'Resumen ejecutivo generado exitosamente', context.taskId)
          completeTask(context.taskId, `Resumen ejecutivo generado para ${variables.target}`)
        }
      } else {
        toast.error('Error generando resumen ejecutivo')
        if (context?.taskId) {
          failTask(context.taskId, 'Error generando resumen ejecutivo')
        }
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const technicalMutation = useMutation({
    mutationFn: (data: { target: string; startDate?: string; endDate?: string }) =>
      reportingAPI.generateTechnicalReport(data.target, data.startDate, data.endDate),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Reporte técnico para ${data.target}`)
      addLog('info', 'reporting', `Generando reporte técnico para ${data.target}`, taskId, `Technical Report - target: ${data.target}`)
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
          completeTask(context.taskId, `Reporte técnico generado para ${variables.target}`)
        }
      } else {
        toast.error('Error generando reporte técnico')
        if (context?.taskId) {
          failTask(context.taskId, 'Error generando reporte técnico')
        }
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const complianceMutation = useMutation({
    mutationFn: (data: { target: string; standard: string; startDate?: string; endDate?: string }) =>
      reportingAPI.generateComplianceReport(data.target, data.standard, data.startDate, data.endDate),
    onMutate: (data) => {
      const taskId = startTask('Reporting', `Reporte de cumplimiento ${data.standard} para ${data.target}`)
      addLog('info', 'reporting', `Generando reporte de cumplimiento ${data.standard} para ${data.target}`, taskId, `Compliance Report - ${data.standard}`)
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
          completeTask(context.taskId, `Reporte de cumplimiento generado para ${variables.target}`)
        }
      } else {
        toast.error('Error generando reporte de cumplimiento')
        if (context?.taskId) {
          failTask(context.taskId, 'Error generando reporte de cumplimiento')
        }
      }
    },
    onError: (error: any, variables, context) => {
      toast.error(`Error: ${error.message}`)
      if (context?.taskId) {
        failTask(context.taskId, error.message)
      }
    }
  })

  const exportMutation = useMutation({
    mutationFn: (data: { reportData: any; format: 'json' | 'html' | 'pdf' }) =>
      reportingAPI.exportReport({ report_data: data.reportData, format: data.format }),
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

