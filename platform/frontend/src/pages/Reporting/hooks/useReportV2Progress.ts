/**
 * Hook para monitorear el progreso de generación de reporte V2
 */

import { useState, useEffect, useRef } from 'react'
import { reportingAPI } from '../../../lib/api/reporting'

interface ReportStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  message?: string
  step?: string
  result?: any
  error?: string
}

export const useReportV2Progress = (taskId: string | null) => {
  const [status, setStatus] = useState<ReportStatus | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const startPolling = () => {
    // #region agent log
    fetch('http://localhost:7242/ingest/cd4b79aa-febd-4ef3-87f4-1622e77b509d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'useReportV2Progress.ts:23',message:'startPolling called',data:{taskId,isPolling},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
    // #endregion
    if (!taskId || isPolling) return
    
    setIsPolling(true)
    
    const poll = async () => {
      try {
        // #region agent log
        fetch('http://localhost:7242/ingest/cd4b79aa-febd-4ef3-87f4-1622e77b509d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'useReportV2Progress.ts:28',message:'Polling API call',data:{taskId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
        // #endregion
        const result = await reportingAPI.getReportStatus(taskId)
        // #region agent log
        fetch('http://localhost:7242/ingest/cd4b79aa-febd-4ef3-87f4-1622e77b509d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'useReportV2Progress.ts:31',message:'Polling API response',data:{taskId,status:result.status,progress:result.progress,error:result.error,rawResult:JSON.stringify(result)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H4'})}).catch(()=>{});
        // #endregion
        
        // Normalizar el status del backend al formato esperado
        const normalizedStatus: ReportStatus = {
          task_id: result.task_id,
          status: result.status === 'pending' ? 'pending' :
                  result.status === 'progress' || result.status === 'processing' ? 'processing' :
                  result.status === 'success' || result.status === 'completed' ? 'completed' :
                  'failed',
          progress: result.progress,
          message: result.message,
          step: (result as any).step,
          result: result.result,
          error: result.error
        }
        
        setStatus(normalizedStatus)
        // #region agent log
        fetch('http://localhost:7242/ingest/cd4b79aa-febd-4ef3-87f4-1622e77b509d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'useReportV2Progress.ts:46',message:'Status normalized and set',data:{normalizedStatus:JSON.stringify(normalizedStatus),willStopPolling:normalizedStatus.status === 'completed' || normalizedStatus.status === 'failed'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H2'})}).catch(()=>{});
        // #endregion
        // Si está completo o falló, detener polling
        if (normalizedStatus.status === 'completed' || normalizedStatus.status === 'failed') {
          stopPolling()
        }
      } catch (error: any) {
        console.error('Error polling report status:', error)
        setStatus({
          task_id: taskId,
          status: 'failed',
          error: error.message || 'Error desconocido al consultar el estado'
        })
        stopPolling()
      }
    }
    
    // Poll inmediatamente y luego cada 2 segundos
    poll()
    intervalRef.current = setInterval(poll, 2000)
  }

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setIsPolling(false)
  }

  useEffect(() => {
    // #region agent log
    fetch('http://localhost:7242/ingest/cd4b79aa-febd-4ef3-87f4-1622e77b509d',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'useReportV2Progress.ts:76',message:'useEffect taskId changed',data:{taskId,willStartPolling:!!taskId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H1'})}).catch(()=>{});
    // #endregion
    if (taskId) {
      startPolling()
    } else {
      stopPolling()
    }
    
    return () => {
      stopPolling()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId])

  return {
    status,
    isPolling,
    startPolling,
    stopPolling
  }
}

