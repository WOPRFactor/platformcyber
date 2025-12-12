import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI } from '../lib/api/auth'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Los interceptores ahora están centralizados en client.ts
  // Verificar autenticación inicial
  useEffect(() => {
    checkAuth()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      console.log('🔐 Iniciando login...')
      setLoading(true)
      const response = await authAPI.login(credentials)

      const { access_token, refresh_token, user } = response

      console.log('✅ Login exitoso, guardando tokens...')
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      console.log('👤 Seteando usuario:', user.username)
      setUser(user)

      console.log('🎉 Login completado exitosamente')
    } catch (error: any) {
      console.error('❌ Login error:', error)
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
        isNetworkError: !error.response
      })
      
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error en el login'
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.code === 'ERR_NETWORK' || !error.response) {
        errorMessage = 'Error de conexión. Verifica que el backend esté funcionando.'
      } else if (error.response?.status === 401) {
        errorMessage = 'Credenciales inválidas'
      } else if (error.response?.status === 403) {
        errorMessage = 'Cuenta deshabilitada'
      } else if (error.response?.status >= 500) {
        errorMessage = 'Error del servidor. Intenta nuevamente más tarde.'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
    }
  }

  const refreshToken = async (): Promise<void> => {
    try {
      const refresh_token = localStorage.getItem('refresh_token')
      if (!refresh_token) throw new Error('No refresh token')

      const response = await authAPI.refresh()

      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)
    } catch (error) {
      console.error('Token refresh error:', error)
      logout()
      throw error
    }
  }

  const checkAuth = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        // Solo mostrar en desarrollo y una vez
        if (process.env.NODE_ENV === 'development' && !window.__authChecked) {
          console.log('🔐 Usuario no autenticado - esperando login')
          window.__authChecked = true
        }
        setLoading(false)
        return
      }

      console.log('Checking authentication with existing token...')
      const user = await authAPI.getCurrentUser()
      if (user && user.username) {
        console.log('Auth check successful:', user.username)
        setUser(user)
      } else {
        console.warn('Auth check returned invalid user data')
        logout()
      }
    } catch (error: any) {
      console.error('Auth check failed:', error.response?.data || error.message)

      // Para cualquier error de autenticación (401, 429, network errors, CORS, etc.)
      // limpiar el estado inmediatamente sin intentar refresh automático
      console.log('🧹 Cleaning up auth state due to authentication error')
      logout()
    } finally {
      setLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    refreshToken,
    checkAuth,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

