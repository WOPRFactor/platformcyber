import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface TargetContextType {
  target: string
  setTarget: (target: string) => void
  clearTarget: () => void
  hasTarget: boolean
}

const TargetContext = createContext<TargetContextType | undefined>(undefined)

export const useTarget = () => {
  const context = useContext(TargetContext)
  if (!context) {
    throw new Error('useTarget must be used within a TargetProvider')
  }
  return context
}

interface TargetProviderProps {
  children: ReactNode
}

export const TargetProvider: React.FC<TargetProviderProps> = ({ children }) => {
  // Estado con persistencia en localStorage
  const [target, setTargetState] = useState<string>(() => {
    return localStorage.getItem('global_target') || ''
  })

  // Función para actualizar target con persistencia
  const setTarget = (newTarget: string) => {
    setTargetState(newTarget)
    localStorage.setItem('global_target', newTarget)
  }

  // Función para limpiar target
  const clearTarget = () => {
    setTargetState('')
    localStorage.removeItem('global_target')
  }

  // Computed property
  const hasTarget = target.trim().length > 0

  // Efecto para sincronizar cambios del localStorage (por si cambia en otra pestaña)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'global_target') {
        setTargetState(e.newValue || '')
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const value: TargetContextType = {
    target,
    setTarget,
    clearTarget,
    hasTarget
  }

  return (
    <TargetContext.Provider value={value}>
      {children}
    </TargetContext.Provider>
  )
}



