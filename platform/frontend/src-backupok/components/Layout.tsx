import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { useNavigate, useLocation } from 'react-router-dom'
import { useConsole } from '../contexts/ConsoleContext'
import ConsoleStatus from './ConsoleStatus'
import ConsoleModal from './ConsoleModal'
import MonitoringConsole from './MonitoringConsole'
import { SystemMonitor } from './systemMonitor'
import ProcessGraphConsole from './ProcessGraphConsole'
import RunningScansConsoleModal from './RunningScansConsoleModal'
import { WorkspaceSelector } from './WorkspaceSelector'
import WebSocketStatus from './WebSocketStatus'
import RightSidebar from './RightSidebar'
import {
  LayoutDashboard,
  Search,
  Brain,
  FileText,
  LogOut,
  User,
  Menu,
  X,
  Network,
  Shield,
  Skull,
  Eye,
  Zap,
  Target,
  AlertTriangle,
  Sword,
  Clock,
  Terminal,
  Activity,
  Link,
  Lock,
  PieChart,
  ScrollText,
  Cloud,
  Container,
  Building2
} from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth()
  const { currentWorkspace } = useWorkspace()
  const { tasks } = useConsole()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [consoleModalOpen, setConsoleModalOpen] = useState(false)
  const [monitoringOpen, setMonitoringOpen] = useState(false)
  const [systemMonitorOpen, setSystemMonitorOpen] = useState(false)
  const [processGraphOpen, setProcessGraphOpen] = useState(false)
  const [runningScansConsoleOpen, setRunningScansConsoleOpen] = useState(false)

  // NOTA: Se eliminó el auto-abrir de consolas para que solo se abran manualmente
  // Las consolas (monitoringOpen, runningScansConsoleOpen, etc.) solo se abren cuando el usuario hace clic en el botón correspondiente

  // Menú superior (header) - Solo iconos
  const topNavigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Integrations', href: '/integrations', icon: Link },
    { name: 'Pentest Selector', href: '/pentest-selector', icon: Shield },
  ]

  // Herramientas de pentesting puro (sidebar)
  const pentestTools = [
    { name: 'Reconnaissance', href: '/reconnaissance', icon: Network },
    { name: 'Scanning', href: '/scanning', icon: Search },
    { name: 'Vulnerability Assessment', href: '/vulnerability', icon: Shield },
    { name: 'Exploitation', href: '/exploitation', icon: Skull },
    { name: 'Post-Exploitation', href: '/post-exploitation', icon: Shield },
    { name: 'Reporting', href: '/reporting', icon: FileText },
  ]

  // Herramientas auxiliares/complementarias (sidebar)
  const auxiliaryTools = [
    { name: 'Whitebox Testing', href: '/whitebox', icon: Eye },
    { name: 'IA Assistant', href: '/ia', icon: Brain },
    { name: 'OWASP Auditor', href: '/owasp', icon: AlertTriangle },
    { name: 'MITRE ATT&CK', href: '/mitre', icon: Sword },
    { name: 'Scheduled Tasks', href: '/scheduled-tasks', icon: Clock },
  ]

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-mono">
      {/* Header */}
      <header className="w-full h-14 flex items-center justify-between px-4 bg-white shadow-md border-b border-gray-200 z-10">
        {/* IZQUIERDA – logo + título */}
        <div className="flex items-center gap-2">
          {/* Botón hamburguesa (solo mobile) */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 rounded-md text-gray-900 hover:bg-gray-100 z-50 relative"
          >
            {sidebarOpen ? <X size={20} className="text-white" /> : <Menu size={20} />}
          </button>

          {/** Logo */}
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            FX
          </div>

          {/** Título */}
          <span className="font-semibold text-gray-900 text-lg">Cybersecurity Suite</span>
        </div>

        {/* WORKSPACE SELECTOR */}
        <div className="hidden md:block ml-6">
          <WorkspaceSelector />
        </div>

        {/* ICONO DASHBOARD */}
        <div className="hidden md:flex items-center ml-8">
          <button
            onClick={() => navigate('/')}
            className={`
              flex items-center justify-center w-10 h-10 rounded-md transition-colors
              ${isActive('/')
                ? 'bg-red-600 text-white shadow-lg'
                : 'text-gray-900 hover:bg-gray-100'
              }
            `}
            title="Dashboard"
          >
            <LayoutDashboard className="w-5 h-5 text-gray-700" />
          </button>
        </div>

        {/* DERECHA – iconos y usuario */}
        <div className="hidden md:flex items-center gap-2">
          <button
            onClick={() => setConsoleModalOpen(true)}
            title="Abrir Consola"
            className="flex items-center justify-center w-10 h-10 rounded-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <Terminal className="w-5 h-5" />
          </button>

          <button
            onClick={() => setMonitoringOpen(!monitoringOpen)}
            title="Monitor de Sistema"
            className="flex items-center justify-center w-10 h-10 rounded-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <Activity className="w-5 h-5" />
          </button>

          <button
            onClick={() => setRunningScansConsoleOpen(!runningScansConsoleOpen)}
            title="Running Scans Console"
            className="flex items-center justify-center w-10 h-10 rounded-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <Zap className="w-5 h-5" />
          </button>

          <button
            onClick={() => setSystemMonitorOpen(!systemMonitorOpen)}
            title="System Monitor - Logs en Tiempo Real"
            className={`
              flex items-center justify-center w-10 h-10 rounded-md transition-colors
              ${systemMonitorOpen
                ? 'bg-red-600 text-white shadow-lg'
                : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }
            `}
          >
            <ScrollText className="w-5 h-5" />
          </button>

          <button
            onClick={() => setProcessGraphOpen(true)}
            title="Gráficos de Procesos"
            className="flex items-center justify-center w-10 h-10 rounded-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <PieChart className="w-5 h-5" />
          </button>

          {/* Separador visual */}
          <div className="w-px h-6 bg-gray-300 mx-1"></div>

          <WebSocketStatus />

          <div className="flex items-center gap-2 text-sm">
            <User className="w-4 h-4 text-gray-600" />
            <span className="text-gray-700 font-medium">{user?.username}</span>
          </div>

          <span className="text-xs bg-red-50 text-red-600 px-2.5 py-1 rounded-full font-medium">{user?.role}</span>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-sm text-gray-700 hover:text-gray-900 transition-colors px-2 py-1 rounded-md hover:bg-gray-50"
          >
            <LogOut className="w-4 h-4" />
            <span>Salir</span>
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`
          fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transform transition-transform duration-300 ease-in-out
          md:translate-x-0 md:static md:inset-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}>
          <div className="flex flex-col h-full pt-16 md:pt-0">
            {/* Usuario en mobile */}
            <div className="md:hidden p-4 border-b border-slate-700">
              <div className="flex items-center space-x-2">
                <User size={16} className="text-slate-400" />
                <span className="text-sm text-slate-300">{user?.username}</span>
                <span className="text-xs bg-red-600 text-white px-2 py-1 rounded">
                  {user?.role}
                </span>
              </div>
            </div>

            {/* Navegación */}
            <nav className="flex-1 px-4 py-6 space-y-4 overflow-y-auto sidebar-scrollbar">
              {/* Herramientas de Pentesting */}
              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3">
                  Pentesting Tools
                </h3>
                {pentestTools.map((item) => {
                  const Icon = item.icon
                  return (
                    <button
                      key={item.name}
                      onClick={() => {
                        navigate(item.href)
                        setSidebarOpen(false)
                      }}
                      className={`
                        w-full flex items-center space-x-3 px-3 py-2 rounded-md text-left transition-colors
                        ${isActive(item.href)
                          ? 'bg-red-600 text-white shadow-lg'
                          : 'text-slate-400 hover:bg-slate-800'
                        }
                      `}
                    >
                      <Icon size={18} className={isActive(item.href) ? 'text-white' : 'text-slate-400'} />
                      <span className="text-sm">{item.name}</span>
                    </button>
                  )
                })}
              </div>

              {/* Separador */}
              <div className="border-t border-slate-700"></div>

              {/* Herramientas Auxiliares */}
              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3">
                  Auxiliary Tools
                </h3>
                {auxiliaryTools.map((item) => {
                  const Icon = item.icon
                  return (
                    <button
                      key={item.name}
                      onClick={() => {
                        navigate(item.href)
                        setSidebarOpen(false)
                      }}
                      className={`
                        w-full flex items-center space-x-3 px-3 py-2 rounded-md text-left transition-colors
                        ${isActive(item.href)
                          ? 'bg-red-600 text-white shadow-lg'
                          : 'text-slate-400 hover:bg-slate-800'
                        }
                      `}
                    >
                      <Icon size={18} className={isActive(item.href) ? 'text-white' : 'text-slate-400'} />
                      <span className="text-sm">{item.name}</span>
                    </button>
                  )
                })}
              </div>
            </nav>

            {/* Footer del sidebar */}
            <div className="p-4 border-t border-slate-700">
              <div className="text-xs text-slate-400">
                <p>Factor X v2.0</p>
                <p>Frontend React + TS</p>
              </div>
            </div>
          </div>
        </aside>

        {/* Overlay para mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Contenido principal */}
        <main className="flex-1 md:ml-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Indicador de estado de consola */}
            <ConsoleStatus />
            {children}
          </div>
        </main>
      </div>

      {/* Modal de consola */}
      <ConsoleModal
        key="console-modal"
        isOpen={consoleModalOpen}
        onClose={() => setConsoleModalOpen(false)}
      />

      {/* Consola de monitoreo */}
      <MonitoringConsole
        key="monitoring-console"
        isOpen={monitoringOpen}
        onClose={() => setMonitoringOpen(false)}
      />

      {/* System Monitor - Logs en tiempo real */}
      <SystemMonitor
        key="system-monitor"
        isOpen={systemMonitorOpen}
        onClose={() => setSystemMonitorOpen(false)}
      />

      {/* Consola de gráficos */}
      <ProcessGraphConsole
        key="process-graph-console"
        isOpen={processGraphOpen}
        onClose={() => setProcessGraphOpen(false)}
      />

      <RunningScansConsoleModal
        isOpen={runningScansConsoleOpen}
        onClose={() => setRunningScansConsoleOpen(false)}
      />

      {/* Barra lateral derecha para accesos especiales */}
      <RightSidebar />
    </div>
  )
}

export default Layout
