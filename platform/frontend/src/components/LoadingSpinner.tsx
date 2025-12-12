import React from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  message?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message = 'Cargando...'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] space-y-4">
      <div className={`${sizeClasses[size]} border-2 border-green-500 border-t-transparent rounded-full animate-spin`}></div>
      {message && (
        <p className="text-green-400 text-sm font-mono animate-pulse">
          {message}
        </p>
      )}
    </div>
  )
}

export default LoadingSpinner


