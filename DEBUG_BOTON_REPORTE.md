# Debug: Botón de Generar Reporte

## Archivos Relacionados

### 1. ReportGenerator.tsx
**Ubicación:** `platform/frontend/src/pages/Reporting/components/ReportGenerator.tsx`

Componente que renderiza los botones de generar reporte.

```tsx
/**
 * Report Generator Component
 * ===========================
 * 
 * Componente para generar reportes según el tipo seleccionado.
 */

import React from 'react'
import { BarChart3, Target, Shield, Loader } from 'lucide-react'
import { UseMutationResult } from '@tanstack/react-query'

interface ReportGeneratorProps {
  activeTab: string
  complianceStandard: string
  executiveMutation: UseMutationResult<any, any, any>
  technicalMutation: UseMutationResult<any, any, any>
  complianceMutation: UseMutationResult<any, any, any>
  onGenerateReport?: (reportType: string) => void
  handleGenerateReport?: (reportType: string) => void // Alias para compatibilidad
}

const ReportGenerator: React.FC<ReportGeneratorProps> = (props) => {
  const {
    activeTab,
    complianceStandard,
    executiveMutation,
    technicalMutation,
    complianceMutation,
    onGenerateReport,
    handleGenerateReport
  } = props

  // Usar onGenerateReport o handleGenerateReport como fallback
  const generateReport = onGenerateReport || handleGenerateReport

  // Handler directo y simple
  const handleGenerateClick = React.useCallback((reportType: string) => {
    console.log('🖱️ CLICK DETECTADO - Tipo:', reportType)
    
    if (!generateReport) {
      console.error('❌ generateReport es undefined')
      alert('Error: Función de generación no disponible')
      return
    }
    
    if (typeof generateReport !== 'function') {
      console.error('❌ generateReport no es función. Tipo:', typeof generateReport)
      alert(`Error: Tipo incorrecto: ${typeof generateReport}`)
      return
    }
    
    console.log('✅ Llamando generateReport con:', reportType)
    generateReport(reportType)
  }, [generateReport])

  return (
    <div className="w-full">
        {activeTab === 'executive' && (
          <div className="mt-4">
            <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Resumen Ejecutivo
                </h3>
                <p className="text-red-600">
                  Reporte de alto nivel para stakeholders y directivos
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  console.log('🖱️ CLICK DIRECTO EN BOTÓN EJECUTIVO')
                  handleGenerateClick('executive')
                }}
                disabled={executiveMutation.isPending}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {executiveMutation.isPending ? (
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <BarChart3 className="w-4 h-4 mr-2" />
                )}
                Generar Resumen Ejecutivo
              </button>
            </div>
          </div>
        )}

        {activeTab === 'technical' && (
          <div className="mt-4">
            <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Reporte Técnico Detallado
                </h3>
                <p className="text-red-600">
                  Reporte técnico completo con todos los hallazgos y metodología
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  console.log('🖱️ CLICK DIRECTO EN BOTÓN TÉCNICO')
                  handleGenerateClick('technical')
                }}
                disabled={technicalMutation.isPending}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {technicalMutation.isPending ? (
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Target className="w-4 h-4 mr-2" />
                )}
                Generar Reporte Técnico
              </button>
            </div>
          </div>
        )}

        {activeTab === 'compliance' && (
          <div className="mt-4">
            <div className="bg-gray-900 border border-red-500 rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Reporte de Cumplimiento - {complianceStandard.toUpperCase()}
                </h3>
                <p className="text-red-600">
                  Evaluación de cumplimiento con estándares de seguridad específicos
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  console.log('🖱️ CLICK DIRECTO EN BOTÓN COMPLIANCE')
                  handleGenerateClick('compliance')
                }}
                disabled={complianceMutation.isPending}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {complianceMutation.isPending ? (
                  <Loader className="w-4 h-4 animate-spin mr-2" />
                ) : (
                  <Shield className="w-4 h-4 mr-2" />
                )}
                Generar Reporte de Cumplimiento
              </button>
            </div>
          </div>
        )}
    </div>
  )
}

export default ReportGenerator
```

---

### 2. Reporting.tsx
**Ubicación:** `platform/frontend/src/pages/Reporting/Reporting.tsx`

Componente padre que pasa la función `handleGenerateReport` al componente hijo.

```tsx
/**
 * Reporting Page
 * ==============
 * 
 * Página principal de reporting refactorizada.
 */

import React, { useState } from 'react'
import { FileText } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { reportingAPI } from '../../lib/api/reporting'
import { toast } from 'sonner'
import { useReportingMutations } from './hooks/useReportingMutations'
import { useWorkspace } from '../../contexts/WorkspaceContext'
import {
  ReportConfig,
  ReportingTabs,
  ReportGenerator,
  GeneratedReport,
  ReportsHistory
} from './components'

const Reporting: React.FC = () => {
  const { currentWorkspace, isLoadingWorkspaces } = useWorkspace()
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [complianceStandard, setComplianceStandard] = useState('general')
  const [exportFormat, setExportFormat] = useState<'json' | 'html' | 'pdf'>('html')
  const [activeTab, setActiveTab] = useState('executive')
  const [generatedReport, setGeneratedReport] = useState<any>(null)

  const {
    executiveMutation,
    technicalMutation,
    complianceMutation,
    exportMutation
  } = useReportingMutations()

  const { data: reports, isLoading: reportsLoading, refetch: refetchReports } = useQuery({
    queryKey: ['reports'],
    queryFn: reportingAPI.listReports,
    enabled: false,
    staleTime: 0,
    cacheTime: 0,
  })

  const handleGenerateReport = React.useCallback((reportType: string) => {
    console.log('🚀 handleGenerateReport llamado:', { reportType, currentWorkspace, startDate, endDate })
    
    if (!currentWorkspace) {
      console.error('❌ No hay workspace seleccionado')
      toast.error('Por favor selecciona un workspace')
      return
    }

    const params = {
      workspaceId: currentWorkspace.id,
      startDate: startDate || undefined,
      endDate: endDate || undefined
    }
    
    console.log('📋 Parámetros para generar reporte:', params)

    switch (reportType) {
      case 'executive':
        executiveMutation.mutate(params, {
          onSuccess: (data) => {
            if (data.success) {
              // Asegurar que el reporte tenga metadata con workspace_id y tipo
              const report = {
                ...data.data,
                metadata: {
                  ...data.data.metadata,
                  workspace_id: currentWorkspace.id,
                  report_type: 'executive',
                  date_from: startDate || undefined,
                  date_to: endDate || undefined
                }
              }
              setGeneratedReport(report)
            }
          }
        })
        break
      case 'technical':
        technicalMutation.mutate(params, {
          onSuccess: (data) => {
            if (data.success) {
              const report = {
                ...data.data,
                metadata: {
                  ...data.data.metadata,
                  workspace_id: currentWorkspace.id,
                  report_type: 'technical',
                  date_from: startDate || undefined,
                  date_to: endDate || undefined
                }
              }
              setGeneratedReport(report)
            }
          }
        })
        break
      case 'compliance':
        complianceMutation.mutate({ ...params, standard: complianceStandard }, {
          onSuccess: (data) => {
            if (data.success) {
              const report = {
                ...data.data,
                metadata: {
                  ...data.data.metadata,
                  workspace_id: currentWorkspace.id,
                  report_type: 'compliance',
                  date_from: startDate || undefined,
                  date_to: endDate || undefined
                }
              }
              setGeneratedReport(report)
            }
          }
        })
        break
      default:
        console.error('❌ Tipo de reporte desconocido:', reportType)
        toast.error(`Tipo de reporte desconocido: ${reportType}`)
    }
  }, [currentWorkspace, startDate, endDate, complianceStandard, executiveMutation, technicalMutation, complianceMutation])

  const handleExportReport = () => {
    if (!generatedReport) {
      toast.error('Primero genere un reporte')
      return
    }

    exportMutation.mutate({
      reportData: generatedReport,
      format: exportFormat
    })
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Reporting</h1>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText className="w-4 h-4" />
          Sistema de reportes profesionales de pentesting
        </div>
      </div>

      {isLoadingWorkspaces ? (
        <div className="bg-gray-800 border border-blue-500 rounded-lg p-6 text-center">
          <p className="text-blue-400">Cargando workspaces...</p>
        </div>
      ) : !currentWorkspace ? (
        <div className="bg-gray-800 border border-yellow-500 rounded-lg p-6 text-center">
          <p className="text-yellow-400">Por favor selecciona un workspace para generar reportes</p>
        </div>
      ) : (
        <>
          <ReportConfig
            startDate={startDate}
            setStartDate={setStartDate}
            endDate={endDate}
            setEndDate={setEndDate}
            complianceStandard={complianceStandard}
            setComplianceStandard={setComplianceStandard}
          />

          <div className="bg-gray-800 border border-green-500 rounded-lg p-6">
            <div className="w-full">
              <ReportingTabs activeTab={activeTab} setActiveTab={setActiveTab} />
              <ReportGenerator
                activeTab={activeTab}
                workspaceName={currentWorkspace.name}
                complianceStandard={complianceStandard}
                executiveMutation={executiveMutation}
                technicalMutation={technicalMutation}
                complianceMutation={complianceMutation}
                onGenerateReport={handleGenerateReport}
              />
            </div>
          </div>
        </>
      )}

      {generatedReport && (
        <GeneratedReport
          generatedReport={generatedReport}
          exportFormat={exportFormat}
          setExportFormat={setExportFormat}
          exportMutation={exportMutation}
          onExportReport={handleExportReport}
        />
      )}

      <ReportsHistory
        reports={reports}
        reportsLoading={reportsLoading}
        onRefresh={() => refetchReports()}
      />
    </div>
  )
}

export default Reporting
```

---

### 3. useReportingMutations.ts
**Ubicación:** `platform/frontend/src/pages/Reporting/hooks/useReportingMutations.ts`

Hook que define las mutations de React Query para generar reportes.

```tsx
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
```

---

## Flujo de Ejecución

1. **Usuario hace click en el botón** (ReportGenerator.tsx línea 72-75)
   ```tsx
   onClick={() => {
     console.log('🖱️ CLICK DIRECTO EN BOTÓN EJECUTIVO')
     handleGenerateClick('executive')
   }}
   ```

2. **handleGenerateClick se ejecuta** (ReportGenerator.tsx línea 37-54)
   ```tsx
   const handleGenerateClick = React.useCallback((reportType: string) => {
     console.log('🖱️ CLICK DETECTADO - Tipo:', reportType)
     generateReport(reportType)  // Llama a la función del padre
   }, [generateReport])
   ```

3. **generateReport es onGenerateReport** (ReportGenerator.tsx línea 34)
   ```tsx
   const generateReport = onGenerateReport || handleGenerateReport
   ```

4. **onGenerateReport viene del padre** (Reporting.tsx línea 180)
   ```tsx
   <ReportGenerator
     onGenerateReport={handleGenerateReport}
     ...
   />
   ```

5. **handleGenerateReport ejecuta la mutation** (Reporting.tsx línea 47-127)
   ```tsx
   const handleGenerateReport = React.useCallback((reportType: string) => {
     switch (reportType) {
       case 'executive':
         executiveMutation.mutate(params, { ... })
         break
     }
   }, [currentWorkspace, startDate, endDate, ...])
   ```

6. **executiveMutation llama a la API** (useReportingMutations.ts línea 18-19)
   ```tsx
   mutationFn: (data) =>
     reportingAPI.generateExecutiveSummary(data.workspaceId, ...)
   ```

---

## Puntos Críticos a Verificar

### 1. ¿Se pasa la función correctamente?
- **Línea 180 de Reporting.tsx:** `onGenerateReport={handleGenerateReport}`
- Verificar que `handleGenerateReport` esté definida antes de pasarla

### 2. ¿La función está definida?
- **Línea 47 de Reporting.tsx:** `const handleGenerateReport = React.useCallback(...)`
- Verificar que todas las dependencias estén correctas

### 3. ¿El click se registra?
- **Línea 72 de ReportGenerator.tsx:** `onClick={() => { ... }}`
- Verificar en consola si aparece `🖱️ CLICK DIRECTO EN BOTÓN EJECUTIVO`

### 4. ¿generateReport es una función?
- **Línea 34 de ReportGenerator.tsx:** `const generateReport = onGenerateReport || handleGenerateReport`
- Si `onGenerateReport` es `undefined`, el botón no funcionará

---

## Logs Esperados en Consola

Al hacer click en el botón, deberías ver en este orden:

1. `🖱️ CLICK DIRECTO EN BOTÓN EJECUTIVO`
2. `🖱️ CLICK DETECTADO - Tipo: executive`
3. `✅ Llamando generateReport con: executive`
4. `🚀 handleGenerateReport llamado: { reportType: 'executive', ... }`
5. `📋 Parámetros para generar reporte: { workspaceId: ..., ... }`

Si falta alguno de estos logs, ahí está el problema.

---

## Posibles Problemas

1. **Si no ves el log #1:** El evento onClick no se está disparando
   - Verificar que el botón no esté deshabilitado
   - Verificar que no haya un elemento sobrepuesto bloqueando el click

2. **Si ves el log #1 pero no el #2:** Problema en `handleGenerateClick`
   - Verificar que `generateReport` esté definida

3. **Si ves los logs #1, #2, #3 pero no el #4:** `generateReport` no es una función
   - Verificar que `onGenerateReport` se esté pasando correctamente desde el padre

4. **Si ves todos los logs pero no pasa nada:** Problema en la mutation o en la API
   - Verificar errores en la consola
   - Verificar que el backend esté corriendo
   - Verificar la respuesta de la API en Network tab

---

## Comandos para Debug

1. **Abrir consola del navegador:** F12
2. **Verificar props del componente:**
   ```javascript
   // En la consola del navegador
   $r.props.onGenerateReport  // Debería ser una función
   ```
3. **Verificar que el botón esté en el DOM:**
   ```javascript
   // En la consola del navegador
   document.querySelector('button:contains("Generar Resumen Ejecutivo")')
   ```
4. **Forzar click desde consola:**
   ```javascript
   // En la consola del navegador
   document.querySelector('button').click()
   ```

---

**Última actualización:** 2025-12-07
**Ambiente:** dev4-improvements

