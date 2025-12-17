import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { toast } from 'sonner'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
  read: boolean
  actionUrl?: string
  actionLabel?: string
  persistent?: boolean
}

interface NotificationContextType {
  notifications: Notification[]
  unreadCount: number
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  removeNotification: (id: string) => void
  clearAll: () => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>(() => {
    // Cargar notificaciones desde localStorage
    const saved = localStorage.getItem('notifications')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        return parsed.map((n: any) => ({
          ...n,
          timestamp: new Date(n.timestamp)
        }))
      } catch {
        return []
      }
    }
    return []
  })

  // Guardar notificaciones en localStorage cuando cambien
  useEffect(() => {
    localStorage.setItem('notifications', JSON.stringify(notifications))
  }, [notifications])

  const unreadCount = notifications.filter(n => !n.read).length

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false
    }

    setNotifications(prev => [newNotification, ...prev])

    // Mostrar toast inmediato
    switch (notification.type) {
      case 'success':
        toast.success(notification.title, {
          description: notification.message,
          action: notification.actionLabel && notification.actionUrl ? {
            label: notification.actionLabel,
            onClick: () => window.open(notification.actionUrl, '_blank')
          } : undefined
        })
        break
      case 'error':
        toast.error(notification.title, {
          description: notification.message,
          action: notification.actionLabel && notification.actionUrl ? {
            label: notification.actionLabel,
            onClick: () => window.open(notification.actionUrl, '_blank')
          } : undefined
        })
        break
      case 'warning':
        toast.warning(notification.title, {
          description: notification.message,
          action: notification.actionLabel && notification.actionUrl ? {
            label: notification.actionLabel,
            onClick: () => window.open(notification.actionUrl, '_blank')
          } : undefined
        })
        break
      case 'info':
        toast.info(notification.title, {
          description: notification.message,
          action: notification.actionLabel && notification.actionUrl ? {
            label: notification.actionLabel,
            onClick: () => window.open(notification.actionUrl, '_blank')
          } : undefined
        })
        break
    }

    // Limpiar notificaciones antiguas (mantener solo las últimas 50)
    setNotifications(prev => prev.slice(0, 50))
  }

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const clearAll = () => {
    setNotifications([])
  }

  // Simular notificaciones del sistema (esto se puede conectar con WebSockets/SSE)
  useEffect(() => {
    const interval = setInterval(() => {
      // Simular notificaciones aleatorias para demo
      const random = Math.random()
      if (random < 0.05) { // 5% de probabilidad cada 30 segundos
        const types: ('success' | 'error' | 'warning' | 'info')[] = ['success', 'error', 'warning', 'info']
        const messages = [
          { title: 'Escaneo completado', message: 'El análisis de vulnerabilidades ha finalizado exitosamente' },
          { title: 'Nueva alerta de seguridad', message: 'Se detectaron vulnerabilidades críticas en el sistema' },
          { title: 'Backup completado', message: 'La copia de seguridad se realizó correctamente' },
          { title: 'Sistema actualizado', message: 'Se aplicaron las últimas actualizaciones de seguridad' },
          { title: 'Conexión perdida', message: 'Se perdió la conexión con el servidor remoto' }
        ]
        const randomMessage = messages[Math.floor(Math.random() * messages.length)]
        const randomType = types[Math.floor(Math.random() * types.length)]

        addNotification({
          type: randomType,
          title: randomMessage.title,
          message: randomMessage.message,
          persistent: randomType === 'error'
        })
      }
    }, 30000) // Cada 30 segundos

    return () => clearInterval(interval)
  }, [addNotification])

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      addNotification,
      markAsRead,
      markAllAsRead,
      removeNotification,
      clearAll
    }}>
      {children}
    </NotificationContext.Provider>
  )
}

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}



