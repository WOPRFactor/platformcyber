import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type Theme = 'dark' | 'light' | 'cyberpunk'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Obtener tema inicial desde localStorage o por defecto 'dark' (no cyberpunk para páginas públicas)
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem('theme')
    // Si no hay tema guardado, usar 'dark' en lugar de 'cyberpunk' para evitar aplicar tema terminal en páginas públicas
    return (saved as Theme) || 'dark'
  })

  // Aplicar tema al documento
  useEffect(() => {
    const root = document.documentElement

    // Remover clases de tema anteriores
    root.classList.remove('theme-dark', 'theme-light', 'theme-cyberpunk')

    // Aplicar nuevo tema
    root.classList.add(`theme-${theme}`)

    // Guardar en localStorage
    localStorage.setItem('theme', theme)

    // Aplicar estilos específicos según tema
    applyThemeStyles(theme)
  }, [theme])

  const applyThemeStyles = (currentTheme: Theme) => {
    const root = document.documentElement

    switch (currentTheme) {
      case 'light':
        root.style.setProperty('--bg-primary', '#ffffff')
        root.style.setProperty('--bg-secondary', '#f8fafc')
        root.style.setProperty('--bg-tertiary', '#e2e8f0')
        root.style.setProperty('--text-primary', '#1e293b')
        root.style.setProperty('--text-secondary', '#64748b')
        root.style.setProperty('--accent-primary', '#3b82f6')
        root.style.setProperty('--accent-secondary', '#1d4ed8')
        root.style.setProperty('--border-color', '#e2e8f0')
        break

      case 'dark':
        root.style.setProperty('--bg-primary', '#0f172a')
        root.style.setProperty('--bg-secondary', '#1e293b')
        root.style.setProperty('--bg-tertiary', '#334155')
        root.style.setProperty('--text-primary', '#f8fafc')
        root.style.setProperty('--text-secondary', '#cbd5e1')
        root.style.setProperty('--accent-primary', '#60a5fa')
        root.style.setProperty('--accent-secondary', '#3b82f6')
        root.style.setProperty('--border-color', '#334155')
        break

      case 'cyberpunk':
      default:
        // Tema cyberpunk actual
        root.style.setProperty('--bg-primary', '#0f172a')
        root.style.setProperty('--bg-secondary', '#1e293b')
        root.style.setProperty('--bg-tertiary', '#334155')
        root.style.setProperty('--text-primary', '#22d3ee')
        root.style.setProperty('--text-secondary', '#67e8f9')
        root.style.setProperty('--accent-primary', '#22d3ee')
        root.style.setProperty('--accent-secondary', '#0891b2')
        root.style.setProperty('--border-color', '#0891b2')
        break
    }
  }

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
  }

  const toggleTheme = () => {
    const themes: Theme[] = ['cyberpunk', 'dark', 'light']
    const currentIndex = themes.indexOf(theme)
    const nextIndex = (currentIndex + 1) % themes.length
    setThemeState(themes[nextIndex])
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}



