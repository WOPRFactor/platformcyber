import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WindowManagerProvider } from '../contexts/WindowManagerContext'
import { ConsoleProvider } from '../contexts/ConsoleContext'
import ProcessGraphConsole from './ProcessGraphConsole'

// Mock Chart.js
vi.mock('react-chartjs-2', () => ({
  Doughnut: () => <div data-testid="doughnut-chart">Doughnut Chart</div>,
  Bar: () => <div data-testid="bar-chart">Bar Chart</div>,
  Line: () => <div data-testid="line-chart">Line Chart</div>
}))

// Mock chart.js
vi.mock('chart.js', () => ({
  Chart: { register: vi.fn() },
  ArcElement: vi.fn(),
  Tooltip: vi.fn(),
  Legend: vi.fn(),
  CategoryScale: vi.fn(),
  LinearScale: vi.fn(),
  BarElement: vi.fn(),
  LineElement: vi.fn(),
  PointElement: vi.fn(),
  Title: vi.fn()
}))

// Mock de los contextos
vi.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { username: 'testuser', role: 'admin' },
    logout: vi.fn()
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}))

vi.mock('../contexts/ConsoleContext', () => ({
  useConsole: () => ({
    tasks: [
      { id: '1', name: 'Reconnaissance', progress: 75, status: 'running' },
      { id: '2', name: 'Scanning', progress: 100, status: 'completed' },
      { id: '3', name: 'Vulnerability', progress: 0, status: 'failed' }
    ],
    logs: [
      { message: 'Task started', type: 'info', timestamp: Date.now() },
      { message: 'Progress updated', type: 'success', timestamp: Date.now() }
    ],
    addLog: vi.fn(),
    startTask: vi.fn(),
    updateTaskProgress: vi.fn(),
    completeTask: vi.fn(),
    failTask: vi.fn(),
    killTask: vi.fn()
  }),
  ConsoleProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ConsoleProvider>
          <WindowManagerProvider>
            {children}
          </WindowManagerProvider>
        </ConsoleProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('ProcessGraphConsole Component', () => {
  it('does not render when closed', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={false} onClose={() => {}} />
      </Wrapper>
    )

    expect(screen.queryByText('Consola de Gráficos')).not.toBeInTheDocument()
  })

  it('renders when open', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={true} onClose={() => {}} />
      </Wrapper>
    )

    expect(screen.getByText('Consola de Gráficos')).toBeInTheDocument()
  })

  it('shows tab navigation', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={true} onClose={() => {}} />
      </Wrapper>
    )

    expect(screen.getByText('Vista General')).toBeInTheDocument()
    expect(screen.getByText('Progreso')).toBeInTheDocument()
    expect(screen.getAllByText('Vulnerabilidades')).toHaveLength(2) // One in tab, one in metrics
    expect(screen.getByText('Descubrimientos')).toBeInTheDocument()
  })

  it('displays task metrics in overview', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={true} onClose={() => {}} />
      </Wrapper>
    )

    expect(screen.getByText('Puertos Abiertos')).toBeInTheDocument()
    expect(screen.getAllByText('Vulnerabilidades')).toHaveLength(2) // One in tab, one in metrics
    expect(screen.getByText('Hosts Escaneados')).toBeInTheDocument()
    expect(screen.getByText('Progreso Global')).toBeInTheDocument()
  })

  it('renders with correct styling', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={true} onClose={() => {}} />
      </Wrapper>
    )

    // Verificar que tenga el modal styling
    const modal = document.querySelector('.bg-gray-900')
    expect(modal).toBeInTheDocument()
  })

  it('has close button in header', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={true} onClose={() => {}} />
      </Wrapper>
    )

    // Verificar que hay un botón de cerrar (ícono X) en el header
    const closeIcon = document.querySelector('.lucide-x')
    expect(closeIcon).toBeInTheDocument()
  })

  it('renders charts in overview tab', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <ProcessGraphConsole isOpen={true} onClose={() => {}} />
      </Wrapper>
    )

    // Verificar que los gráficos se renderizan
    expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument()
  })
})
