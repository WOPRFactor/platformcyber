import React, { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate, useLocation } from 'react-router-dom'
import { Link, Shield, Cloud, Container, Building2, ChevronLeft } from 'lucide-react'

interface RightSidebarProps {}

const RightSidebar: React.FC<RightSidebarProps> = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)
  const [tooltipPosition, setTooltipPosition] = useState<{ top: number; left: number } | null>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const itemRefs = useRef<{ [key: string]: HTMLDivElement | null }>({})

  const specialAccessTools = [
    { name: 'Integrations', href: '/integrations', icon: Link },
    { name: 'Pentest Selector', href: '/pentest-selector', icon: Shield },
    { name: 'Cloud Pentesting', href: '/cloud', icon: Cloud },
    { name: 'Container Security', href: '/container', icon: Container },
    { name: 'Active Directory', href: '/active-directory', icon: Building2 },
  ]

  const isActive = (href: string) => location.pathname === href

  const handleMouseEnter = () => {
    // Cancelar cualquier timeout pendiente
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    setIsOpen(true)
  }

  const handleMouseLeave = () => {
    // Esperar un pequeño delay antes de cerrar para evitar cierres accidentales
    timeoutRef.current = setTimeout(() => {
      setIsOpen(false)
      timeoutRef.current = null
    }, 200) // 200ms de delay
  }

  // Limpiar timeout al desmontar el componente
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <>
      {/* Botón Trigger - Fijo en el borde derecho */}
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className={`
          fixed right-0 top-1/2 -translate-y-1/2 z-40
          w-10 h-16 bg-slate-900 border-l border-y border-slate-800 rounded-l-lg
          flex items-center justify-center
          transition-all duration-300 ease-in-out
          hover:bg-slate-800 shadow-lg cursor-pointer
          ${isOpen ? 'translate-x-16' : 'translate-x-0'}
        `}
        title="Accesos especiales"
      >
        <ChevronLeft className="w-5 h-5 text-slate-400" />
      </div>

      {/* Panel Flotante */}
      <aside
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className={`
          fixed right-0 top-0 h-full z-50 w-16 bg-slate-900 border-l border-slate-800
          transform transition-transform duration-300 ease-in-out
          shadow-2xl
          ${isOpen ? 'translate-x-0' : 'translate-x-full'}
        `}
        style={{ overflow: 'visible', overflowY: 'auto' }}
      >
        <div className="flex flex-col h-full pt-16">
          {/* Header del panel */}
          <div className="px-2 py-4 border-b border-slate-800">
            <div className="w-12 h-12 mx-auto bg-red-600/20 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-red-400" />
            </div>
          </div>

          {/* Lista de iconos */}
          <nav className="flex-1 px-2 py-4 space-y-2 overflow-y-auto sidebar-scrollbar" style={{ overflowX: 'visible' }}>
            {specialAccessTools.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              const isHovered = hoveredItem === item.name
              
              return (
                <div
                  key={item.name}
                  className="relative"
                  style={{ position: 'relative', overflow: 'visible' }}
                  ref={(el) => {
                    itemRefs.current[item.name] = el
                  }}
                  onMouseEnter={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect()
                    const position = {
                      top: rect.top + rect.height / 2,
                      left: rect.left - 8
                    }
                    setTooltipPosition(position)
                    setHoveredItem(item.name)
                  }}
                  onMouseLeave={() => {
                    setHoveredItem(null)
                    setTooltipPosition(null)
                  }}
                >
                  <button
                    onClick={() => {
                      navigate(item.href)
                      // Cancelar timeout y cerrar inmediatamente
                      if (timeoutRef.current) {
                        clearTimeout(timeoutRef.current)
                        timeoutRef.current = null
                      }
                      setIsOpen(false)
                    }}
                    className={`
                      w-12 h-12 mx-auto rounded-lg
                      flex items-center justify-center
                      transition-all duration-200
                      relative z-10
                      ${active
                        ? 'bg-red-600 text-white shadow-lg'
                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                      }
                    `}
                  >
                    <Icon 
                      size={20} 
                      className={active ? 'text-white' : 'text-slate-400'} 
                    />
                  </button>
                </div>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="px-2 py-4 border-t border-slate-800">
            <div className="w-12 h-12 mx-auto bg-slate-800 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-slate-500" />
            </div>
          </div>
        </div>
      </aside>

      {/* Tooltip usando Portal para renderizar fuera del contenedor con overflow */}
      {hoveredItem && tooltipPosition && typeof document !== 'undefined' && createPortal(
        <div
          className="fixed pointer-events-none"
          style={{
            top: `${tooltipPosition.top}px`,
            left: `${tooltipPosition.left}px`,
            transform: 'translate(-100%, -50%)',
            whiteSpace: 'nowrap',
            zIndex: 99999,
            pointerEvents: 'none'
          }}
        >
          <div 
            className="bg-slate-800 text-white text-xs font-medium px-3 py-1.5 rounded-lg shadow-2xl border border-slate-700 relative"
            style={{
              backgroundColor: '#1e293b',
              color: '#ffffff'
            }}
          >
            {specialAccessTools.find(t => t.name === hoveredItem)?.name}
            {/* Flecha del tooltip */}
            <div
              className="absolute left-full top-1/2 -translate-y-1/2"
              style={{
                width: 0,
                height: 0,
                borderStyle: 'solid',
                borderWidth: '4px 0 4px 6px',
                borderColor: 'transparent transparent transparent #1e293b'
              }}
            ></div>
          </div>
        </div>,
        document.body
      )}
    </>
  )
}

export default RightSidebar

