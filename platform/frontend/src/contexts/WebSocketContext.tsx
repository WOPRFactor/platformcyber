/**
 * WebSocket Context
 * =================
 * 
 * Maneja conexión y eventos de Socket.IO en toda la aplicación.
 */

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

// Types
interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  joinWorkspace: (workspaceId: number) => void;
  leaveWorkspace: (workspaceId: number) => void;
  joinScan: (scanId: string) => void;
  leaveScan: (scanId: string) => void;
  addEventListener: (event: string, handler: (...args: any[]) => void) => void;
  removeEventListener: (event: string, handler: (...args: any[]) => void) => void;
}

interface ScanProgressEvent {
  scan_id: string;
  workspace_id: number;
  progress: number;
  status: string;
  message: string;
  timestamp: number;
  data?: any;
}

interface NotificationEvent {
  workspace_id: number;
  title: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  timestamp: number;
  data?: any;
}

interface VulnerabilityEvent {
  workspace_id: number;
  vulnerability: {
    name: string;
    severity: string;
    description?: string;
    [key: string]: any;
  };
  scan_id?: string;
  timestamp: number;
}

interface TaskUpdateEvent {
  task_id: string;
  workspace_id: number;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE';
  progress?: number;
  result?: any;
  error?: string;
  timestamp: number;
}

// Create context
const WebSocketContext = createContext<WebSocketContextType | null>(null);

// Provider props
interface WebSocketProviderProps {
  children: ReactNode;
  url?: string;
}

// Detectar URL del backend (misma lógica que client.ts)
// DEV4-IMPROVEMENTS: Puerto 5001 para entorno de mejoras
const isProductionEnv = import.meta.env.VITE_ENV === 'prod'
const defaultWebSocketURL = isProductionEnv 
  ? 'http://192.168.0.11:5002'
  : 'http://192.168.0.11:5001'  // Puerto 5001 para dev4-improvements

/**
 * WebSocket Provider Component
 */
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ 
  children, 
  url = defaultWebSocketURL 
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize socket connection
  useEffect(() => {
    console.log('🔌 DEV4 Initializing WebSocket connection to:', url);
    console.log('🔌 Expected port: 5001');

    const newSocket = io(url, {
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      timeout: 20000,
    });

    // Connection events
    newSocket.on('connect', () => {
      console.log('✅ WebSocket connected:', newSocket.id);
      setIsConnected(true);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason);
      setIsConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      setIsConnected(false);
    });

    newSocket.on('connection_established', (data) => {
      console.log('🎉 Connection established:', data);
    });

    // Ping/Pong for keep-alive
    const pingInterval = setInterval(() => {
      if (newSocket.connected) {
        newSocket.emit('ping');
      }
    }, 25000);

    newSocket.on('pong', (data) => {
      console.log('🏓 Pong received:', new Date(data.timestamp * 1000));
    });

    setSocket(newSocket);

    // Cleanup
    return () => {
      clearInterval(pingInterval);
      newSocket.close();
    };
  }, [url]);

  // Join workspace room
  const joinWorkspace = useCallback((workspaceId: number) => {
    if (socket && isConnected) {
      console.log(`👥 Joining workspace: ${workspaceId}`);
      socket.emit('join_workspace', { workspace_id: workspaceId });
    }
  }, [socket, isConnected]);

  // Leave workspace room
  const leaveWorkspace = useCallback((workspaceId: number) => {
    if (socket && isConnected) {
      console.log(`👋 Leaving workspace: ${workspaceId}`);
      socket.emit('leave_workspace', { workspace_id: workspaceId });
    }
  }, [socket, isConnected]);

  // Join scan room
  const joinScan = useCallback((scanId: string) => {
    if (socket && isConnected) {
      console.log(`🔍 Joining scan: ${scanId}`);
      socket.emit('join_scan', { scan_id: scanId });
    }
  }, [socket, isConnected]);

  // Leave scan room
  const leaveScan = useCallback((scanId: string) => {
    if (socket && isConnected) {
      console.log(`🚪 Leaving scan: ${scanId}`);
      socket.emit('leave_scan', { scan_id: scanId });
    }
  }, [socket, isConnected]);

  // Add event listener
  const addEventListener = useCallback((event: string, handler: (...args: any[]) => void) => {
    if (socket) {
      socket.on(event, handler);
    }
  }, [socket]);

  // Remove event listener
  const removeEventListener = useCallback((event: string, handler: (...args: any[]) => void) => {
    if (socket) {
      socket.off(event, handler);
    }
  }, [socket]);

  const value: WebSocketContextType = {
    socket,
    isConnected,
    joinWorkspace,
    leaveWorkspace,
    joinScan,
    leaveScan,
    addEventListener,
    removeEventListener,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

/**
 * Custom hook to use WebSocket context
 */
export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

/**
 * Custom hook for scan progress events
 */
export const useScanProgress = (
  workspaceId: number | null,
  onProgress?: (event: ScanProgressEvent) => void
) => {
  const { socket, isConnected, joinWorkspace, leaveWorkspace } = useWebSocket();
  const [progress, setProgress] = useState<ScanProgressEvent | null>(null);

  useEffect(() => {
    if (!socket || !isConnected || !workspaceId) return;

    joinWorkspace(workspaceId);

    const handleProgress = (event: ScanProgressEvent) => {
      console.log('📊 Scan progress:', event);
      setProgress(event);
      onProgress?.(event);
    };

    socket.on('scan_progress', handleProgress);

    return () => {
      socket.off('scan_progress', handleProgress);
      leaveWorkspace(workspaceId);
    };
  }, [socket, isConnected, workspaceId, joinWorkspace, leaveWorkspace, onProgress]);

  return progress;
};

/**
 * Custom hook for notifications
 */
export const useNotifications = (
  workspaceId: number | null,
  onNotification?: (event: NotificationEvent) => void
) => {
  const { socket, isConnected, joinWorkspace, leaveWorkspace } = useWebSocket();
  const [notifications, setNotifications] = useState<NotificationEvent[]>([]);

  useEffect(() => {
    if (!socket || !isConnected || !workspaceId) return;

    joinWorkspace(workspaceId);

    const handleNotification = (event: NotificationEvent) => {
      console.log(`🔔 Notification [${event.level}]:`, event.title);
      setNotifications(prev => [...prev, event]);
      onNotification?.(event);
    };

    socket.on('notification', handleNotification);

    return () => {
      socket.off('notification', handleNotification);
      leaveWorkspace(workspaceId);
    };
  }, [socket, isConnected, workspaceId, joinWorkspace, leaveWorkspace, onNotification]);

  return notifications;
};

/**
 * Custom hook for vulnerability alerts
 */
export const useVulnerabilityAlerts = (
  workspaceId: number | null,
  onVulnerability?: (event: VulnerabilityEvent) => void
) => {
  const { socket, isConnected, joinWorkspace, leaveWorkspace } = useWebSocket();
  const [vulnerabilities, setVulnerabilities] = useState<VulnerabilityEvent[]>([]);

  useEffect(() => {
    if (!socket || !isConnected || !workspaceId) return;

    joinWorkspace(workspaceId);

    const handleVulnerability = (event: VulnerabilityEvent) => {
      console.log(`🚨 Vulnerability found [${event.vulnerability.severity}]:`, event.vulnerability.name);
      setVulnerabilities(prev => [...prev, event]);
      onVulnerability?.(event);
    };

    socket.on('vuln_found', handleVulnerability);

    return () => {
      socket.off('vuln_found', handleVulnerability);
      leaveWorkspace(workspaceId);
    };
  }, [socket, isConnected, workspaceId, joinWorkspace, leaveWorkspace, onVulnerability]);

  return vulnerabilities;
};

/**
 * Custom hook for task updates
 */
export const useTaskUpdates = (
  workspaceId: number | null,
  onTaskUpdate?: (event: TaskUpdateEvent) => void
) => {
  const { socket, isConnected, joinWorkspace, leaveWorkspace } = useWebSocket();
  const [tasks, setTasks] = useState<Map<string, TaskUpdateEvent>>(new Map());

  useEffect(() => {
    if (!socket || !isConnected || !workspaceId) return;

    joinWorkspace(workspaceId);

    const handleTaskUpdate = (event: TaskUpdateEvent) => {
      console.log(`📋 Task update [${event.status}]:`, event.task_id);
      setTasks(prev => new Map(prev).set(event.task_id, event));
      onTaskUpdate?.(event);
    };

    socket.on('task_update', handleTaskUpdate);

    return () => {
      socket.off('task_update', handleTaskUpdate);
      leaveWorkspace(workspaceId);
    };
  }, [socket, isConnected, workspaceId, joinWorkspace, leaveWorkspace, onTaskUpdate]);

  return Array.from(tasks.values());
};

// Export types
export type {
  WebSocketContextType,
  ScanProgressEvent,
  NotificationEvent,
  VulnerabilityEvent,
  TaskUpdateEvent,
};

