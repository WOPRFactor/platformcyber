import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Terminal, Eye, EyeOff, AlertCircle } from 'lucide-react'

const Login: React.FC = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    console.log('🔐 Intentando login con:', { username: credentials.username, password: '***' })

    try {
      console.log('📡 Enviando petición de login...')
      await login(credentials)
      console.log('✅ Login exitoso, redirigiendo...')
      navigate('/')
    } catch (err: any) {
      console.error('❌ Error en login:', err)
      console.error('Detalles del error:', {
        message: err.message,
        response: err.response?.data,
        stack: err.stack
      })
      setError(err.message || 'Error de autenticación')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
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
      {/* Banner de Testing - Fijo en la parte superior */}
      <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-black py-2 px-4 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2">
          <span className="font-bold text-lg animate-pulse">⚠️</span>
          <span className="font-bold text-lg">PLATAFORMA DE TESTING - DEV4-IMPROVEMENTS</span>
          <span className="font-bold text-lg animate-pulse">⚠️</span>
        </div>
      </div>

      <div className="max-w-md w-full mt-16">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center border-4 border-yellow-300">
              <Terminal className="w-8 h-8 text-black" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-yellow-400 mb-2">
            Factor X
          </h1>
          <p className="text-yellow-600 mb-2">
            Cybersecurity Suite v2.0
          </p>
          {/* Badge de Testing */}
          <div className="inline-flex items-center gap-2 bg-yellow-500/20 border-2 border-yellow-500 rounded-full px-4 py-1">
            <span className="text-yellow-400 font-bold text-sm">🧪 TESTING ENVIRONMENT</span>
          </div>
        </div>

        {/* Login Form */}
        <div className="card border-2 border-yellow-500/30">
          <h2 className="text-xl font-bold text-yellow-400 mb-6 text-center">
            Acceso al Sistema
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-yellow-400 mb-1">
                Usuario
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={credentials.username}
                onChange={handleChange}
                className="input w-full"
                placeholder="admin"
                required
                autoComplete="username"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-yellow-400 mb-1">
                Contraseña
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={credentials.password}
                  onChange={handleChange}
                  className="input w-full pr-10"
                  placeholder="••••••••"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-yellow-600 hover:text-yellow-400"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center space-x-2 text-red-400 bg-red-900/20 border border-red-500 rounded p-3">
                <AlertCircle size={16} />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Autenticando...' : 'Acceder al Sistema'}
            </button>
          </form>

          {/* Info adicional */}
          <div className="mt-6 pt-4 border-t border-yellow-500/20">
            <div className="text-xs text-yellow-600 text-center space-y-1">
              <p>Usuario por defecto: <span className="text-yellow-400">admin</span></p>
              <p>Contraseña: <span className="text-yellow-400">admin123</span></p>
              <p className="text-yellow-400 font-bold">🧪 Ambiente de Testing - Dev4-Improvements</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-xs text-yellow-600">
          <p>Frontend React + TypeScript | Backend Flask + JWT</p>
          <p>Seguridad Empresarial | Factor X 🤖</p>
          <p className="mt-2 font-bold text-yellow-400">⚠️ TESTING ENVIRONMENT - NO PRODUCTION ⚠️</p>
        </div>
      </div>
    </div>
  )
}

export default Login
