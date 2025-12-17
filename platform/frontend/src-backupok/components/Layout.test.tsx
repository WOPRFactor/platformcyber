import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WindowManagerProvider } from '../contexts/WindowManagerContext'
import { ConsoleProvider } from '../contexts/ConsoleContext'
import Layout from './Layout'

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
    tasks: [],
    startTask: vi.fn(),
    addLog: vi.fn(),
    updateTaskProgress: vi.fn(),
    completeTask: vi.fn(),
    failTask: vi.fn(),
    killTask: vi.fn()
  }),
  ConsoleProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>
}))

vi.mock('./GlobalSearch', () => ({
  default: () => <div className="w-72"><input placeholder="Buscar módulos, páginas..." /></div>
}))

vi.mock('./ThemeSelector', () => ({
  default: () => <div data-testid="theme-selector">Theme Selector</div>
}))

vi.mock('./ConsoleModal', () => ({
  default: ({ isOpen }: { isOpen: boolean }) =>
    isOpen ? <div data-testid="console-modal">Console Modal</div> : null
}))

vi.mock('./MonitoringConsole', () => ({
  default: ({ isOpen }: { isOpen: boolean }) =>
    isOpen ? <div data-testid="monitoring-console">Monitoring Console</div> : null
}))

vi.mock('./ConsoleStatus', () => ({
  default: () => <div data-testid="console-status">Console Status</div>
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

describe('Layout Component', () => {
  it('renders header with logo and title', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </Wrapper>
    )

    // Verificar que el logo esté presente
    expect(screen.getByText('FX')).toBeInTheDocument()

    // Verificar que el título esté presente
    expect(screen.getByText('Cybersecurity Suite')).toBeInTheDocument()

    // Verificar que el contenido se renderice
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('renders navigation buttons', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </Wrapper>
    )

    // Verificar que los botones de navegación estén presentes
    expect(screen.getByTitle('Dashboard')).toBeInTheDocument()
    expect(screen.getByTitle('Integrations')).toBeInTheDocument()
    expect(screen.getByTitle('Pentest Selector')).toBeInTheDocument()
  })

  it('renders utility components', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </Wrapper>
    )

    // Verificar que los componentes de utilidad estén presentes
    expect(screen.getByPlaceholderText(/Buscar módulos, páginas/)).toBeInTheDocument()
    expect(screen.getByTestId('theme-selector')).toBeInTheDocument()
    expect(screen.getByTestId('console-status')).toBeInTheDocument()
  })

  it('shows user information', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </Wrapper>
    )

    // Verificar información del usuario
    const userElements = screen.getAllByText('testuser')
    expect(userElements.length).toBeGreaterThan(0)

    // Buscar el badge de admin específicamente
    const adminBadge = screen.getByText('admin', { selector: '.admin-badge' })
    expect(adminBadge).toBeInTheDocument()
  })

  it('renders console modal when opened', () => {
    const Wrapper = createWrapper()

    render(
      <Wrapper>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </Wrapper>
    )

    // El modal debería estar cerrado por defecto
    expect(screen.queryByTestId('console-modal')).not.toBeInTheDocument()
    expect(screen.queryByTestId('monitoring-console')).not.toBeInTheDocument()
  })
})
