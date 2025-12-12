import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import {
  Activity, Shield, AlertTriangle,
  CheckCircle, Clock, Zap
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
  RealTimeActivity
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
    if (!healthData?.system_info) return null

    const backendInfo = healthData.system_info
    return {
      cpu_count: backendInfo.cpu_percent || 0,
      memory: {
        available: (backendInfo.memory_total_mb - backendInfo.memory_used_mb) * 1024 * 1024,
        percent: backendInfo.memory_percent || 0,
        total: backendInfo.memory_total_mb * 1024 * 1024
      },
      disk: {
        free: backendInfo.disk_usage_percent ? (100 - backendInfo.disk_usage_percent) : 0,
        percent: backendInfo.disk_usage_percent || 0,
        total: 100
      },
      platform: backendInfo.platform || 'Unknown',
      python_version: backendInfo.python_version || 'Unknown'
    }
  }, [healthData])

  // Calcular métricas avanzadas
  const activeScans = scanSessions?.filter(s => s.status === 'running').length || 0
  const totalScans = scanSessions?.length || 0
  const completedAudits = owaspAudits?.audits?.filter((a: any) => a.status === 'completed').length || 0
  const totalVulnerabilities = scanSessions?.reduce((sum, s) => sum + (s.vulnerabilities || 0), 0) || 0
  const avgScanTime = scanSessions?.length ?
    scanSessions.reduce((sum, s) => sum + ((s as any).duration || 0), 0) / scanSessions.length : 0

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
      color: healthData?.status === 'healthy' ? 'text-green-400' : 'text-red-400',
      bgColor: healthData?.status === 'healthy' ? 'bg-green-500/10' : 'bg-red-500/10',
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
      subtitle: `${totalScans} total realizados`
    },
    {
      title: 'Vulnerabilidades',
      value: totalVulnerabilities.toString(),
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      trend: totalVulnerabilities > 10 ? 'Crítico' : totalVulnerabilities > 5 ? 'Alto' : 'Bajo',
      subtitle: 'Necesitan atención'
    },
    {
      title: 'Auditorías OWASP',
      value: completedAudits.toString(),
      icon: CheckCircle,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      trend: completedAudits > 0 ? 'Completadas' : null,
      subtitle: 'Top 10 evaluado'
    },
    {
      title: 'Tiempo Promedio',
      value: avgScanTime > 0 ? `${Math.round(avgScanTime)}min` : 'N/A',
      icon: Clock,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      trend: avgScanTime < 30 ? 'Excelente' : avgScanTime < 60 ? 'Bueno' : 'Mejorar',
      subtitle: 'Por escaneo completo'
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
        <VulnerabilityPieChart data={vulnerabilityData} total={totalVulnerabilities} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SystemInfo systemInfo={systemInfo} isLoading={healthLoading} />
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
    </div>
  )
}

export default Dashboard
