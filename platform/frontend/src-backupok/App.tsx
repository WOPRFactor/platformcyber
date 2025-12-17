import React, { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom'
import { Terminal } from 'lucide-react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { TargetProvider } from './contexts/TargetContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { ConsoleProvider } from './contexts/ConsoleContext'
import { WorkspaceProvider } from './contexts/WorkspaceContext'
import { WindowManagerProvider } from './contexts/WindowManagerContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import DashboardEnhanced from './pages/DashboardEnhanced'
import Scanning from './pages/Scanning'
import IA from './pages/IA'
import Reconnaissance from './pages/Reconnaissance'
import VulnerabilityAssessment from './pages/VulnerabilityAssessment'
import Exploitation from './pages/Exploitation'
import PostExploitation from './pages/PostExploitation'
import WhiteboxTesting from './pages/WhiteboxTesting'
import Integrations from './pages/Integrations'
import ReportingV2 from './pages/ReportingV2'
import PentestSelector from './pages/PentestSelector'
import OwaspAuditor from './pages/OwaspAuditor'
import MitreAttacks from './pages/MitreAttacks'
import ScheduledTasks from './pages/ScheduledTasks'
import RealTerminal from './pages/RealTerminal'
import Cloud from './pages/Cloud'
import ContainerSecurity from './pages/Container'
import ActiveDirectory from './pages/ActiveDirectory'
import Layout from './components/Layout'
import LoadingSpinner from './components/LoadingSpinner'
import RealTimeNotifications from './components/RealTimeNotifications'
import './App.css'

// Crear cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Componente de rutas protegidas
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading, user } = useAuth()

  console.log('🔒 ProtectedRoute - Loading:', loading, 'Authenticated:', isAuthenticated, 'User:', user?.username)

  if (loading) {
    console.log('⏳ ProtectedRoute: Mostrando loading spinner')
    return <LoadingSpinner />
  }

  if (isAuthenticated) {
    console.log('✅ ProtectedRoute: Usuario autenticado, renderizando children')
    return <>{children}</>
  } else {
    console.log('❌ ProtectedRoute: Usuario no autenticado, redirigiendo a login')
    return <Navigate to="/" />
  }
}

// Componente de rutas públicas
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner />
  }

  return !isAuthenticated ? <>{children}</> : <Navigate to="/" />
}

// Página de bienvenida
function WelcomePage() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner />
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" />
  }

  return (
    <div 
      className="min-h-screen flex items-center justify-center px-4" 
      style={{ 
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        backgroundColor: '#111827',
        color: '#ffffff'
      }}
    >
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <Terminal className="mx-auto h-16 w-16 text-red-400" />
          <h1 className="mt-4 text-2xl font-semibold text-gray-900" style={{ color: '#ffffff' }}>
            Cybersecurity Suite
          </h1>
          <p className="mt-2" style={{ color: '#9ca3af' }}>
            Factor X - Plataforma de Pentesting Avanzada
          </p>
        </div>

        <div className="space-y-4">
          <Link
            to="/force-login"
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            style={{ textDecoration: 'none' }}
          >
            🔐 Acceder al Sistema
          </Link>

          <div className="text-sm" style={{ color: '#6b7280' }}>
            <p>Credenciales de prueba:</p>
            <p>Usuario: <code className="px-1 rounded" style={{ backgroundColor: '#1f2937', color: '#ffffff' }}>admin</code></p>
            <p>Contraseña: <code className="px-1 rounded" style={{ backgroundColor: '#1f2937', color: '#ffffff' }}>admin123</code></p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Componente para forzar login (acceso directo)
function ForceLoginRoute({ children }: { children: React.ReactNode }) {
  // Limpiar cualquier token existente para forzar login
  useEffect(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }, [])

  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/force-login"
        element={
          <ForceLoginRoute>
            <Login />
          </ForceLoginRoute>
        }
      />
      <Route path="/terminal" element={<RealTerminal />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/dashboard" element={<DashboardEnhanced />} />
                <Route path="/dashboard-old" element={<Dashboard />} />
                <Route path="/reconnaissance" element={<Reconnaissance />} />
                <Route path="/scanning" element={<Scanning />} />
                <Route path="/vulnerability" element={<VulnerabilityAssessment />} />
                <Route path="/exploitation" element={<Exploitation />} />
                <Route path="/post-exploitation" element={<PostExploitation />} />
                <Route path="/whitebox" element={<WhiteboxTesting />} />
                <Route path="/integrations" element={<Integrations />} />
                <Route path="/reporting" element={<ReportingV2 />} />
                <Route path="/pentest-selector" element={<PentestSelector />} />
                <Route path="/ia" element={<IA />} />
                <Route path="/owasp" element={<OwaspAuditor />} />
                <Route path="/mitre" element={<MitreAttacks />} />
                <Route path="/scheduled-tasks" element={<ScheduledTasks />} />
                <Route path="/cloud" element={<Cloud />} />
                <Route path="/container" element={<ContainerSecurity />} />
                <Route path="/active-directory" element={<ActiveDirectory />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TargetProvider>
          <AppWithConditionalProviders />
        </TargetProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

// Componente que usa useAuth dentro del contexto del AuthProvider
function AppWithConditionalProviders() {
  const { isAuthenticated } = useAuth()

  const content = (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <AppRoutes />
      </div>
    </Router>
  )

  if (isAuthenticated) {
    // Usar la misma URL que el cliente API
    // DEV4-IMPROVEMENTS: Puerto 5001 para entorno de mejoras
    const isProductionEnv = import.meta.env.VITE_ENV === 'prod'
    const websocketURL = isProductionEnv 
      ? 'http://192.168.0.11:5002' 
      : 'http://192.168.0.11:5001'  // Puerto 5001 para dev4-improvements
    
    return (
      <ThemeProvider>
        <WorkspaceProvider>
          <WebSocketProvider url={websocketURL}>
            <ConsoleProvider>
              <WindowManagerProvider>
                <RealTimeNotifications />
                {content}
              </WindowManagerProvider>
            </ConsoleProvider>
          </WebSocketProvider>
        </WorkspaceProvider>
      </ThemeProvider>
    )
  }

  return content
}

export default App
