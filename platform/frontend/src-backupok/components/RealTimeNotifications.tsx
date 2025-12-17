/**
 * Real-Time Notifications Component
 * ==================================
 * 
 * Componente que muestra notificaciones en tiempo real vía WebSocket.
 */

import React, { useEffect, useState } from 'react';
import { useNotifications, NotificationEvent } from '../contexts/WebSocketContext';
import { useWorkspace } from '../contexts/WorkspaceContext';

interface NotificationItemProps {
  notification: NotificationEvent;
  onClose: () => void;
}

const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Auto-dismiss después de 5 segundos
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Wait for fade-out animation
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const getLevelColor = () => {
    switch (notification.level) {
      case 'success':
        return 'bg-red-600';
      case 'warning':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  const getLevelIcon = () => {
    switch (notification.level) {
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div
      className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        mb-2 p-4 rounded-xl shadow-lg backdrop-blur-sm
        ${getLevelColor()} bg-opacity-90 text-white
        max-w-md
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{getLevelIcon()}</span>
          <div className="flex-1">
            <h4 className="font-semibold text-sm">{notification.title}</h4>
            <p className="text-xs mt-1 opacity-90">{notification.message}</p>
            <p className="text-xs mt-1 opacity-70">
              {new Date(notification.timestamp * 1000).toLocaleTimeString()}
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
          }}
          className="text-white hover:text-gray-200 ml-2"
        >
          ×
        </button>
      </div>
    </div>
  );
};

/**
 * Real-Time Notifications Container
 */
export const RealTimeNotifications: React.FC = () => {
  const { currentWorkspace } = useWorkspace();
  const workspaceId = currentWorkspace?.id || null;
  
  const [displayedNotifications, setDisplayedNotifications] = useState<NotificationEvent[]>([]);
  
  // Subscribe to notifications
  const notifications = useNotifications(workspaceId, (notification) => {
    // Opcional: trigger sonido o vibración
    console.log('New notification:', notification);
  });

  // Update displayed notifications (mantener solo las últimas 5)
  useEffect(() => {
    setDisplayedNotifications(notifications.slice(-5));
  }, [notifications]);

  const handleClose = (index: number) => {
    setDisplayedNotifications(prev => prev.filter((_, i) => i !== index));
  };

  if (displayedNotifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {displayedNotifications.map((notification, index) => (
        <NotificationItem
          key={`${notification.timestamp}-${index}`}
          notification={notification}
          onClose={() => handleClose(index)}
        />
      ))}
    </div>
  );
};

export default RealTimeNotifications;

