import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, X, FileText, Network, Shield, Brain, AlertTriangle, Sword, Target, Clock } from 'lucide-react'
import { cn } from '../lib/utils'

interface SearchResult {
  id: string
  title: string
  description: string
  type: 'page' | 'module' | 'scan' | 'report' | 'vulnerability'
  url: string
  icon: React.ComponentType<any>
  module: string
}

interface GlobalSearchProps {
  className?: string
}

const GlobalSearch: React.FC<GlobalSearchProps> = ({ className }) => {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const searchRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Datos de búsqueda simulados - en producción esto vendría de una API
  const searchData: SearchResult[] = [
    // Páginas principales
    {
      id: 'dashboard',
      title: 'Dashboard',
      description: 'Vista general del sistema y métricas',
      type: 'page',
      url: '/dashboard',
      icon: FileText,
      module: 'Sistema'
    },
    {
      id: 'reconnaissance',
      title: 'Reconnaissance',
      description: 'Análisis de reconocimiento y recopilación de información',
      type: 'module',
      url: '/reconnaissance',
      icon: Network,
      module: 'Reconocimiento'
    },
    {
      id: 'scanning',
      title: 'Scanning',
      description: 'Escaneo de puertos y servicios',
      type: 'module',
      url: '/scanning',
      icon: Search,
      module: 'Escaneo'
    },
    {
      id: 'vulnerability',
      title: 'Vulnerability Assessment',
      description: 'Análisis de vulnerabilidades del sistema',
      type: 'module',
      url: '/vulnerability',
      icon: Shield,
      module: 'Vulnerabilidades'
    },
    {
      id: 'reporting',
      title: 'Reporting',
      description: 'Generación y gestión de reportes',
      type: 'module',
      url: '/reporting',
      icon: FileText,
      module: 'Reportes'
    },
    {
      id: 'ia',
      title: 'Inteligencia Artificial',
      description: 'Análisis inteligente con IA',
      type: 'module',
      url: '/ia',
      icon: Brain,
      module: 'IA'
    },
    {
      id: 'owasp',
      title: 'OWASP Auditor',
      description: 'Auditoría de estándares OWASP',
      type: 'module',
      url: '/owasp',
      icon: AlertTriangle,
      module: 'OWASP'
    },
    {
      id: 'mitre',
      title: 'MITRE ATT&CK',
      description: 'Marco de amenazas MITRE ATT&CK',
      type: 'module',
      url: '/mitre',
      icon: Sword,
      module: 'MITRE'
    },
    {
      id: 'scheduled-tasks',
      title: 'Tareas Programadas',
      description: 'Gestión de tareas automatizadas',
      type: 'module',
      url: '/scheduled-tasks',
      icon: Clock,
      module: 'Automatización'
    },
    {
      id: 'pentest-selector',
      title: 'Pentest Selector',
      description: 'Selector de metodologías de pentesting',
      type: 'module',
      url: '/pentest-selector',
      icon: Target,
      module: 'Metodologías'
    }
  ]

  // Función de búsqueda
  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    setIsLoading(true)

    // Simular búsqueda asíncrona
    await new Promise(resolve => setTimeout(resolve, 200))

    const filteredResults = searchData.filter(item =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.module.toLowerCase().includes(searchQuery.toLowerCase())
    )

    setResults(filteredResults.slice(0, 8)) // Limitar a 8 resultados
    setIsLoading(false)
  }

  // Efecto para búsqueda en tiempo real
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      performSearch(query)
    }, 300) // Debounce de 300ms

    return () => clearTimeout(timeoutId)
  }, [query])

  // Manejar clicks fuera del componente
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setQuery('')
        setResults([])
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Atajos de teclado
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === '/' && event.target === document.body) {
        event.preventDefault()
        inputRef.current?.focus()
        setIsOpen(true)
      }

      if (event.key === 'Escape') {
        setIsOpen(false)
        setQuery('')
        setResults([])
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  const handleResultClick = (result: SearchResult) => {
    navigate(result.url)
    setIsOpen(false)
    setQuery('')
    setResults([])
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'page': return 'text-blue-600 bg-blue-100'
      case 'module': return 'text-emerald-700 bg-emerald-50'
      case 'scan': return 'text-purple-600 bg-purple-100'
      case 'report': return 'text-orange-600 bg-orange-100'
      case 'vulnerability': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div ref={searchRef} className={cn("relative", className)}>
      {/* Input de búsqueda */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-500" />
        </div>
        <input
          ref={inputRef}
          type="text"
          placeholder="Buscar módulos, páginas... (presiona /)"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          className="block w-80 pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('')
              setResults([])
            }}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <X className="h-5 w-5 text-gray-500 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Resultados de búsqueda */}
      {isOpen && (query || results.length > 0) && (
        <div className="absolute z-50 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200 max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-2">Buscando...</p>
            </div>
          ) : results.length > 0 ? (
            <div>
              {results.map((result) => {
                const Icon = result.icon
                return (
                  <button
                    key={result.id}
                    onClick={() => handleResultClick(result)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <Icon className="h-5 w-5 text-gray-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {result.title}
                          </p>
                          <span className={cn(
                            "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium",
                            getTypeColor(result.type)
                          )}>
                            {result.type}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {result.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {result.module}
                        </p>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          ) : query ? (
            <div className="p-4 text-center text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No se encontraron resultados para "{query}"</p>
              <p className="text-sm mt-1">Intenta con otros términos</p>
            </div>
          ) : (
            <div className="p-4">
              <p className="text-sm text-gray-500 mb-2">Búsqueda rápida</p>
              <div className="space-y-1">
                {searchData.slice(0, 5).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleResultClick(item)}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded"
                  >
                    {item.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Footer con atajos */}
          <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Presiona ↑↓ para navegar</span>
              <span>Enter para seleccionar</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GlobalSearch



