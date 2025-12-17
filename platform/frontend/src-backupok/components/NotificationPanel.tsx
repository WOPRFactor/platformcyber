import React from 'react'
import { Bell, X, Check, CheckCheck, ExternalLink, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'
import { useNotifications } from '../contexts/NotificationContext'
import { cn } from '../lib/utils'

interface NotificationPanelProps {
  className?: string
}

const NotificationPanel: React.FC<NotificationPanelProps> = ({ className }) => {
  const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification, clearAll } = useNotifications()

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-gray-800" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'info':
      default:
        return <Info className="w-5 h-5 text-blue-500" />
    }
  }

  const formatTime = (timestamp: Date) => {
    const now = new Date()
    const diff = now.getTime() - timestamp.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  return (
    <div className={cn("relative", className)}>
      <button
        className="relative p-2 text-gray-500 hover:text-gray-600 transition-colors"
        title="Notifications"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Panel de notificaciones */}
      <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Notifications
          </h3>
          <div className="flex items-center space-x-2">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                title="Mark all as read"
              >
                <CheckCheck className="w-4 h-4" />
                <span>Mark all read</span>
              </button>
            )}
            {notifications.length > 0 && (
              <button
                onClick={clearAll}
                className="text-sm text-gray-500 hover:text-gray-700"
                title="Clear all"
              >
                Clear all
              </button>
            )}
          </div>
        </div>

        {/* Lista de notificaciones */}
        <div className="max-h-80 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No notifications yet</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={cn(
                  "flex items-start space-x-3 p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors",
                  !notification.read && "bg-blue-50"
                )}
              >
                {/* Icono */}
                <div className="flex-shrink-0 mt-0.5">
                  {getIcon(notification.type)}
                </div>

                {/* Contenido */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatTime(notification.timestamp)}
                      </p>
                    </div>

                    {/* Acciones */}
                    <div className="flex items-center space-x-1 ml-2">
                      {notification.actionUrl && notification.actionLabel && (
                        <button
                          onClick={() => window.open(notification.actionUrl, '_blank')}
                          className="p-1 text-blue-600 hover:text-blue-700"
                          title={notification.actionLabel}
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      )}
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="p-1 text-gray-500 hover:text-gray-600"
                          title="Mark as read"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => removeNotification(notification.id)}
                        className="p-1 text-gray-500 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-400"
                        title="Remove"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Indicador de no leído */}
                {!notification.read && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2"></div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        {notifications.length > 0 && (
          <div className="p-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-200">
            <p className="text-xs text-gray-500 dark:text-gray-500 text-center">
              {unreadCount} unread • {notifications.length} total
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default NotificationPanel



