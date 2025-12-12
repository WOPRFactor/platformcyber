/**
 * Chart Data Utilities
 * =====================
 * 
 * Utilidades para generar datos de gráficos Chart.js.
 */

import { Task, Log } from '../../../contexts/ConsoleContext'

interface PentestMetrics {
  openPorts: number
  vulnerabilities: {
    critical: number
    high: number
    medium: number
    low: number
  }
  scannedHosts: number
  discoveredServices: number
  foundUrls: number
  sensitiveFiles: number
  scanProgress: number
}

export const generateProgressData = (tasks: Task[]) => {
  const activeTasks = tasks.filter(task =>
    task.status === 'running' ||
    (task.status === 'completed' && Date.now() - task.startTime.getTime() < 300000)
  )

  return {
    labels: activeTasks.length > 0 ? activeTasks.map(task => task.name) : ['Sin tareas activas'],
    datasets: [{
      label: 'Progreso (%)',
      data: activeTasks.length > 0 ? activeTasks.map(task => task.progress) : [0],
      backgroundColor: activeTasks.map(task => {
        if (task.status === 'completed') return 'rgba(34, 197, 94, 0.8)'
        if (task.status === 'running') return 'rgba(59, 130, 246, 0.8)'
        if (task.status === 'failed') return 'rgba(239, 68, 68, 0.8)'
        return 'rgba(156, 163, 175, 0.8)'
      }),
      borderColor: activeTasks.map(task => {
        if (task.status === 'completed') return 'rgba(34, 197, 94, 1)'
        if (task.status === 'running') return 'rgba(59, 130, 246, 1)'
        if (task.status === 'failed') return 'rgba(239, 68, 68, 1)'
        return 'rgba(156, 163, 175, 1)'
      }),
      borderWidth: 2,
    }],
  }
}

export const generateVulnerabilityData = (metrics: PentestMetrics) => ({
  labels: ['Críticas', 'Altas', 'Medias', 'Bajas'],
  datasets: [{
    data: [
      metrics.vulnerabilities.critical,
      metrics.vulnerabilities.high,
      metrics.vulnerabilities.medium,
      metrics.vulnerabilities.low,
    ],
    backgroundColor: [
      'rgba(239, 68, 68, 0.8)',
      'rgba(245, 101, 101, 0.8)',
      'rgba(251, 191, 36, 0.8)',
      'rgba(34, 197, 94, 0.8)',
    ],
    borderColor: [
      'rgba(239, 68, 68, 1)',
      'rgba(245, 101, 101, 1)',
      'rgba(251, 191, 36, 1)',
      'rgba(34, 197, 94, 1)',
    ],
    borderWidth: 2,
  }],
})

export const generateDiscoveryData = (metrics: PentestMetrics) => ({
  labels: ['Puertos Abiertos', 'Servicios', 'URLs', 'Archivos Sensibles'],
  datasets: [{
    label: 'Descubrimientos',
    data: [
      metrics.openPorts,
      metrics.discoveredServices,
      metrics.foundUrls,
      metrics.sensitiveFiles
    ],
    backgroundColor: [
      'rgba(59, 130, 246, 0.8)',
      'rgba(168, 85, 247, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(239, 68, 68, 0.8)',
    ],
    borderColor: [
      'rgba(59, 130, 246, 1)',
      'rgba(168, 85, 247, 1)',
      'rgba(34, 197, 94, 1)',
      'rgba(239, 68, 68, 1)',
    ],
    borderWidth: 2,
  }],
})

export const generateDiscoveryHistoryData = (logs: Log[]) => {
  const now = Date.now()
  const labels = []
  const portsHistory = []
  const vulnHistory = []
  const urlsHistory = []

  for (let i = 5; i >= 0; i--) {
    const timePoint = new Date(now - i * 10 * 60 * 1000)
    labels.push(i === 0 ? 'Ahora' : `Hace ${i * 10}m`)

    const intervalLogs = logs.filter(log =>
      log.timestamp.getTime() >= timePoint.getTime() - 10 * 60 * 1000 &&
      log.timestamp.getTime() < timePoint.getTime()
    )

    let portsInInterval = 0
    let vulnsInInterval = 0
    let urlsInInterval = 0

    intervalLogs.forEach(log => {
      const message = log.message.toLowerCase()
      if (message.includes('puerto') && message.includes('abierto')) portsInInterval++
      if (message.includes('vulnerabilidad') || message.includes('exploit')) vulnsInInterval++
      if (message.includes('url') || message.includes('endpoint')) urlsInInterval++
    })

    portsHistory.push(portsInInterval)
    vulnHistory.push(vulnsInInterval)
    urlsHistory.push(urlsInInterval)
  }

  return {
    labels,
    datasets: [
      {
        label: 'Puertos Abiertos',
        data: portsHistory,
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Vulnerabilidades',
        data: vulnHistory,
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
      {
        label: 'URLs Encontradas',
        data: urlsHistory,
        borderColor: 'rgba(34, 197, 94, 1)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
    ],
  }
}

export const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        color: '#e5e7eb',
        font: {
          size: 12,
        },
      },
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#e5e7eb',
      bodyColor: '#e5e7eb',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        color: '#9ca3af',
      },
      grid: {
        color: 'rgba(156, 163, 175, 0.2)',
      },
    },
    x: {
      ticks: {
        color: '#9ca3af',
      },
      grid: {
        color: 'rgba(156, 163, 175, 0.2)',
      },
    },
  },
}


