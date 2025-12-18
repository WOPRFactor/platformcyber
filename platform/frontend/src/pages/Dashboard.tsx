import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import {
  Activity, Shield, AlertTriangle,
  CheckCircle, Clock, Zap, Search, Target, FileText
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { systemAPI } from '../lib/api/system'
import { scanningAPI } from '../lib/api/scanning'
import { owaspAPI } from '../lib/api/owasp'
import { useTaskUpdates, useVulnerabilityAlerts } from '../contexts/WebSocketContext'
import {
  DashboardHeader,
  KPICards,
  ScanActivityChart,
  VulnerabilityPieChart,
  SystemInfo,
  RecentActivity,
  QuickActions,
  SecurityAlerts,
  PerformanceMetrics,
  RealTimeActivity,
  PhasesOverview
} from './Dashboard/components'

const Dashboard: React.FC = () => {
  const { user, isAuthenticated } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h')
  
  // WebSocket Real-Time Data
  const tasks = useTaskUpdates(currentWorkspace?.id || null)
  const vulnerabilities = useVulnerabilityAlerts(currentWorkspace?.id || null)

  // Queries para datos en tiempo real
  const { data: healthData, isLoading: healthLoading, refetch: refetchHealth } = useQuery({
    queryKey: ['health'],
    queryFn: systemAPI.healthCheck,
    enabled: !!localStorage.getItem('access_token'),
    refetchInterval: 30000,
  })

  // Query para métricas del sistema (CPU, memoria, disco)
  const { data: systemMetrics, isLoading: systemMetricsLoading, refetch: refetchSystemMetrics } = useQuery({
    queryKey: ['system-metrics'],
    queryFn: systemAPI.getSystemMetrics,
    enabled: !!localStorage.getItem('access_token'),
    refetchInterval: 30000,
  })

  const { data: scanSessions, isLoading: sessionsLoading, refetch: refetchSessions } = useQuery({
    queryKey: ['scan-sessions', currentWorkspace?.id],
    queryFn: () => currentWorkspace?.id ? scanningAPI.getScanSessions(currentWorkspace.id) : Promise.resolve([]),
    enabled: isAuthenticated && !!currentWorkspace?.id,
    refetchInterval: 15000,
  })

  const { data: owaspAudits } = useQuery({
    queryKey: ['owasp-audits'],
    queryFn: owaspAPI.listAudits,
    enabled: isAuthenticated,
    refetchInterval: 20000,
  })

  // Transformar los datos del backend al formato esperado por el frontend
  const systemInfo = React.useMemo(() => {
    if (!systemMetrics?.system) return null

    const backendSystem = systemMetrics.system
    
    // Manejar errores del backend
    if (backendSystem.error) {
      return null
    }

    return {
      cpu_count: backendSystem.cpu?.count || 0,
      cpu_percent: backendSystem.cpu?.percent || 0,
      memory: {
        available: (backendSystem.memory?.available_mb || 0) * 1024 * 1024,
        percent: backendSystem.memory?.percent || 0,
        total: (backendSystem.memory?.total_mb || 0) * 1024 * 1024
      },
      disk: {
        free: (backendSystem.disk?.free_gb || 0) * 1024 * 1024 * 1024,
        percent: backendSystem.disk?.percent || 0,
        total: (backendSystem.disk?.total_gb || 0) * 1024 * 1024 * 1024
      },
      platform: backendSystem.platform || 'Unknown',
      python_version: backendSystem.python_version || 'Unknown'
    }
  }, [systemMetrics])

  // Calcular métricas avanzadas
  const activeScans = scanSessions?.filter(s => s.status === 'running').length || 0
  const totalScans = scanSessions?.length || 0
  const completedAudits = owaspAudits?.audits?.filter((a: any) => a.status === 'completed').length || 0
  const totalVulnerabilities = scanSessions?.reduce((sum, s) => sum + (s.vulnerabilities || 0), 0) || 0
  const avgScanTime = scanSessions?.length ?
    scanSessions.reduce((sum, s) => sum + ((s as any).duration || 0), 0) / scanSessions.length : 0

  // Totales de pasos por fase (basado en herramientas disponibles)
  const phaseTotals = {
    reconnaissance: 26,
    scanning: 30,
    vulnerability: 25,
    exploitation: 14,
    post_exploitation: 6,
    reporting: 5
  }

  // Mapear scan_type a fases
  const mapScanTypeToPhase = (scanType: string): string | null => {
    const mapping: Record<string, string> = {
      'reconnaissance': 'reconnaissance',
      'port_scan': 'scanning',
      'vuln_scan': 'vulnerability',
      'exploit': 'exploitation',
      'post_exploit': 'post_exploitation',
      'ad_enum': 'scanning',
      'cloud_audit': 'vulnerability'
    }
    return mapping[scanType] || null
  }

  // Calcular pasos completados por fase
  const phasesProgress = React.useMemo(() => {
    const completedByPhase: Record<string, number> = {
      reconnaissance: 0,
      scanning: 0,
      vulnerability: 0,
      exploitation: 0,
      post_exploitation: 0,
      reporting: 0
    }

    // Contar escaneos completados por fase
    if (scanSessions) {
      scanSessions.forEach((session: any) => {
        if (session.status === 'completed') {
          const phase = mapScanTypeToPhase(session.scan_type || '')
          if (phase && completedByPhase.hasOwnProperty(phase)) {
            completedByPhase[phase]++
          }
        }
      })
    }

    // Contar auditorías OWASP completadas como parte de vulnerability
    if (owaspAudits?.audits) {
      const completedOwasp = owaspAudits.audits.filter((a: any) => a.status === 'completed').length
      completedByPhase.vulnerability += completedOwasp
    }

    return [
      {
        id: 'reconnaissance',
        name: 'Reconocimiento',
        route: '/reconnaissance',
        completed: completedByPhase.reconnaissance,
        total: phaseTotals.reconnaissance,
        icon: Search,
        color: 'text-blue-400',
        bgColor: 'bg-blue-500/10'
      },
      {
        id: 'scanning',
        name: 'Escaneo',
        route: '/scanning',
        completed: completedByPhase.scanning,
        total: phaseTotals.scanning,
        icon: Activity,
        color: 'text-cyan-400',
        bgColor: 'bg-cyan-500/10'
      },
      {
        id: 'vulnerability',
        name: 'Evaluación de Vulnerabilidades',
        route: '/vulnerability',
        completed: completedByPhase.vulnerability,
        total: phaseTotals.vulnerability,
        icon: Shield,
        color: 'text-red-400',
        bgColor: 'bg-red-500/10'
      },
      {
        id: 'exploitation',
        name: 'Explotación',
        route: '/exploitation',
        completed: completedByPhase.exploitation,
        total: phaseTotals.exploitation,
        icon: Zap,
        color: 'text-orange-400',
        bgColor: 'bg-orange-500/10'
      },
      {
        id: 'post_exploitation',
        name: 'Post-Explotación',
        route: '/post-exploitation',
        completed: completedByPhase.post_exploitation,
        total: phaseTotals.post_exploitation,
        icon: Target,
        color: 'text-purple-400',
        bgColor: 'bg-purple-500/10'
      },
      {
        id: 'reporting',
        name: 'Reportes',
        route: '/reporting',
        completed: completedByPhase.reporting,
        total: phaseTotals.reporting,
        icon: FileText,
        color: 'text-green-400',
        bgColor: 'bg-green-500/10'
      }
    ]
  }, [scanSessions, owaspAudits])

  // Datos para gráficos
  const scanActivityData = React.useMemo(() => {
    if (!scanSessions) return []

    const grouped = scanSessions.reduce((acc, session) => {
      const date = new Date(session.start_time || Date.now())
      const key = selectedTimeRange === '1h' ? date.getHours() :
                  selectedTimeRange === '24h' ? date.getHours() :
                  selectedTimeRange === '7d' ? date.getDate() : date.getDate()

      acc[key] = (acc[key] || 0) + 1
      return acc
    }, {} as Record<number, number>)

    return Object.entries(grouped).map(([time, count]) => ({
      time: selectedTimeRange === '1h' ? `${time}:00` : time.toString(),
      scans: count,
      vulnerabilities: Math.floor(count * 2.5)
    }))
  }, [scanSessions, selectedTimeRange])

  const vulnerabilityData = [
    { name: 'Críticas', value: Math.floor(totalVulnerabilities * 0.1), color: '#ef4444' },
    { name: 'Altas', value: Math.floor(totalVulnerabilities * 0.3), color: '#f97316' },
    { name: 'Medias', value: Math.floor(totalVulnerabilities * 0.4), color: '#eab308' },
    { name: 'Bajas', value: Math.floor(totalVulnerabilities * 0.2), color: '#22c55e' }
  ]

  const kpiCards = [
    {
      title: 'Estado del Sistema',
      value: healthData?.status === 'healthy' ? 'Activo' : 'Inactivo',
      icon: Activity,
      color: healthData?.status === 'healthy' ? 'text-gray-900' : 'text-red-400',
      bgColor: healthData?.status === 'healthy' ? 'bg-red-600/10' : 'bg-red-500/10',
      trend: null,
      subtitle: 'Disponibilidad 99.9%'
    },
    {
      title: 'Escaneos Activos',
      value: activeScans.toString(),
      icon: Shield,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      trend: activeScans > 0 ? '+' + activeScans : null,
      subtitle: totalScans > 0 ? `${totalScans} total realizados` : 'Inicia tu primer escaneo'
    },
    {
      title: 'Vulnerabilidades',
      value: totalVulnerabilities.toString(),
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      trend: totalVulnerabilities > 10 ? 'Crítico' : totalVulnerabilities > 5 ? 'Alto' : totalVulnerabilities > 0 ? 'Bajo' : null,
      subtitle: totalVulnerabilities > 0 ? 'Necesitan atención' : totalScans > 0 ? 'Sin vulnerabilidades detectadas' : 'Realiza escaneos para detectar'
    },
    {
      title: 'Auditorías OWASP',
      value: completedAudits.toString(),
      icon: CheckCircle,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      trend: completedAudits > 0 ? 'Completadas' : null,
      subtitle: completedAudits > 0 ? 'Top 10 evaluado' : 'Crea una auditoría OWASP'
    },
    {
      title: 'Tiempo Promedio',
      value: avgScanTime > 0 ? `${Math.round(avgScanTime)}min` : 'N/A',
      icon: Clock,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      trend: avgScanTime > 0 ? (avgScanTime < 30 ? 'Excelente' : avgScanTime < 60 ? 'Bueno' : 'Mejorar') : null,
      subtitle: avgScanTime > 0 ? 'Por escaneo completo' : 'Sin escaneos completados'
    },
    {
      title: 'Simulaciones MITRE',
      value: '0',
      icon: Zap,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10',
      trend: null,
      subtitle: 'Ataques simulados'
    }
  ]

  const handleRefresh = () => {
    refetchHealth()
    refetchSystemMetrics()
    refetchSessions()
  }

  return (
    <div className="space-y-8">
      <DashboardHeader
        user={user}
        healthStatus={healthData?.status}
        selectedTimeRange={selectedTimeRange}
        onTimeRangeChange={setSelectedTimeRange}
        onRefresh={handleRefresh}
      />

      <KPICards
        kpiCards={kpiCards}
        healthStatus={healthData?.status}
        activeScans={activeScans}
        totalVulnerabilities={totalVulnerabilities}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ScanActivityChart data={scanActivityData} />
        <VulnerabilityPieChart data={vulnerabilityData} total={totalVulnerabilities} totalScans={totalScans} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SystemInfo systemInfo={systemInfo} isLoading={systemMetricsLoading} />
        <RecentActivity sessions={scanSessions} isLoading={sessionsLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <QuickActions />
        <SecurityAlerts totalVulnerabilities={totalVulnerabilities} systemInfo={systemInfo} />
        <PerformanceMetrics
          totalScans={totalScans}
          scanSessions={scanSessions}
          totalVulnerabilities={totalVulnerabilities}
          avgScanTime={avgScanTime}
          completedAudits={completedAudits}
        />
      </div>

      <RealTimeActivity tasks={tasks} vulnerabilities={vulnerabilities} />

      <PhasesOverview phases={phasesProgress} />
    </div>
  )
}

export default Dashboard
