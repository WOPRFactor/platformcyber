import React from 'react'
import { Sun, Moon, Zap, ChevronDown } from 'lucide-react'
import { useTheme, Theme } from '../contexts/ThemeContext'
import { cn } from '../lib/utils'

interface ThemeSelectorProps {
  className?: string
}

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ className }) => {
  const { theme, setTheme } = useTheme()
  const [isOpen, setIsOpen] = React.useState(false)

  const themes = [
    {
      id: 'cyberpunk' as Theme,
      name: 'Cyberpunk',
      icon: Zap,
      description: 'Tema cyber con neón',
      preview: 'bg-gradient-to-r from-cyan-500 to-blue-500'
    },
    {
      id: 'dark' as Theme,
      name: 'Dark',
      icon: Moon,
      description: 'Tema oscuro moderno',
      preview: 'bg-gray-900'
    },
    {
      id: 'light' as Theme,
      name: 'Light',
      icon: Sun,
      description: 'Tema claro profesional',
      preview: 'bg-gray-100'
    }
  ]

  const currentTheme = themes.find(t => t.id === theme) || themes[0]

  return (
    <div className={cn("relative", className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        title="Cambiar tema"
      >
        <currentTheme.icon className="w-5 h-5" />
        <ChevronDown className="w-4 h-4" />
      </button>

      {/* Dropdown de temas */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">
              Seleccionar Tema
            </h3>
          </div>

          <div className="p-2">
            {themes.map((themeOption) => {
              const Icon = themeOption.icon
              const isSelected = themeOption.id === theme

              return (
                <button
                  key={themeOption.id}
                  onClick={() => {
                    setTheme(themeOption.id)
                    setIsOpen(false)
                  }}
                  className={cn(
                    "w-full flex items-center space-x-3 p-3 rounded-md text-left transition-colors",
                    isSelected
                      ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                      : "hover:bg-gray-50 dark:hover:bg-gray-700"
                  )}
                >
                  {/* Preview del tema */}
                  <div className={cn(
                    "w-8 h-8 rounded-full border-2 border-gray-300 dark:border-gray-600 flex items-center justify-center",
                    themeOption.preview
                  )}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>

                  {/* Información del tema */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {themeOption.name}
                      </p>
                      {isSelected && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      )}
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {themeOption.description}
                    </p>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Footer con información */}
          <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Tema actual: <span className="font-medium">{currentTheme.name}</span>
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ThemeSelector



