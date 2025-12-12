/**
 * Scan Progress Monitor Component
 * ================================
 * 
 * Componente para monitorear progreso de scans en tiempo real.
 */

import React from 'react';
import { useScanProgress, ScanProgressEvent } from '../contexts/WebSocketContext';
import { useWorkspace } from '../contexts/WorkspaceContext';

interface ScanProgressBarProps {
  progress: number;
  status: string;
  message: string;
}

const ScanProgressBar: React.FC<ScanProgressBarProps> = ({ progress, status, message }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-red-600';
      case 'failed':
        return 'bg-red-500';
      case 'running':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      case 'running':
        return '🔄';
      default:
        return '⏸️';
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-xl">{getStatusIcon()}</span>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-600">
            {message || 'Processing...'}
          </span>
        </div>
        <span className="text-sm font-semibold text-gray-700 dark:text-gray-600">
          {progress}%
        </span>
      </div>
      
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full ${getStatusColor()} transition-all duration-300 ease-out rounded-full relative overflow-hidden`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        >
          {/* Animated shimmer effect */}
          {status === 'running' && progress < 100 && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer" />
          )}
        </div>
      </div>
      
      <div className="mt-1 text-xs text-gray-500 dark:text-gray-500 capitalize">
        Status: {status}
      </div>
    </div>
  );
};

interface ScanProgressMonitorProps {
  scanId?: string;
  onComplete?: (event: ScanProgressEvent) => void;
}

/**
 * Scan Progress Monitor Component
 */
export const ScanProgressMonitor: React.FC<ScanProgressMonitorProps> = ({ 
  scanId, 
  onComplete 
}) => {
  const { currentWorkspace } = useWorkspace();
  const workspaceId = currentWorkspace?.id || null;
  
  const progress = useScanProgress(workspaceId, (event) => {
    console.log('Scan progress update:', event);
    
    // Si el scan está completo y hay un callback
    if (event.status === 'completed' && onComplete) {
      onComplete(event);
    }
  });

  // Si hay un scanId específico, filtrar solo ese scan
  const relevantProgress = scanId && progress?.scan_id !== scanId ? null : progress;

  if (!relevantProgress) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-white rounded-xl shadow-md p-4 mb-4">
      <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">
        Scan Progress: {relevantProgress.scan_id}
      </h3>
      
      <ScanProgressBar
        progress={relevantProgress.progress}
        status={relevantProgress.status}
        message={relevantProgress.message}
      />
      
      {/* Información adicional */}
      {relevantProgress.data && (
        <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs">
          <pre className="text-gray-700 dark:text-gray-600 overflow-x-auto">
            {JSON.stringify(relevantProgress.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ScanProgressMonitor;

