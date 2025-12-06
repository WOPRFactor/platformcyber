import React, { createContext, useContext, useState, useCallback, useRef, ReactNode } from 'react'

// Contexto para manejar el z-index de las ventanas
interface WindowManagerContextType {
  getZIndex: (windowId: string) => number
  bringToFront: (windowId: string) => void
  setWindowActive: (windowId: string) => void
}

const WindowManagerContext = createContext<WindowManagerContextType | null>(null)

export const useWindowManager = () => {
  const context = useContext(WindowManagerContext)
  if (!context) {
    throw new Error('useWindowManager must be used within a WindowManagerProvider')
  }
  return context
}

export const WindowManagerProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [windowZIndexes, setWindowZIndexes] = useState<Record<string, number>>({})
  const baseZIndex = 1000 // Z-index base para que todas estén al frente
  const nextZIndex = useRef(baseZIndex)

  const getZIndex = useCallback((windowId: string) => {
    return windowZIndexes[windowId] || baseZIndex
  }, [windowZIndexes])

  const bringToFront = useCallback((windowId: string) => {
    // Aumentar ligeramente el z-index de la ventana clickeada
    // para que aparezca por encima de las otras, pero todas siguen visibles
    nextZIndex.current += 1
    setWindowZIndexes(prev => ({
      ...prev,
      [windowId]: nextZIndex.current
    }))
  }, [])

  const setWindowActive = useCallback((windowId: string) => {
    bringToFront(windowId)
  }, [bringToFront])

  return (
    <WindowManagerContext.Provider value={{ getZIndex, bringToFront, setWindowActive }}>
      {children}
    </WindowManagerContext.Provider>
  )
}
