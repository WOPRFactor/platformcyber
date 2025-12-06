/**
 * WebSocket Status Indicator
 * ===========================
 * 
 * Muestra el estado de la conexión WebSocket en el navbar.
 */

import React, { useState } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';

export const WebSocketStatus: React.FC = () => {
  const { isConnected, socket } = useWebSocket();
  const [showDetails, setShowDetails] = useState(false);

  const getStatusColor = () => {
    return isConnected ? 'bg-green-500' : 'bg-red-500';
  };

  const getStatusText = () => {
    return isConnected ? 'Connected' : 'Disconnected';
  };

  const getStatusIcon = () => {
    return isConnected ? '🟢' : '🔴';
  };

  return (
    <div className="relative">
      {/* Status Indicator */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className={`
          flex items-center space-x-2 px-3 py-1.5 rounded-full
          text-xs font-medium transition-all duration-200
          ${isConnected 
            ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
            : 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
          }
        `}
        title={`WebSocket ${getStatusText()}`}
      >
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${getStatusColor()} opacity-75`}></span>
          <span className={`relative inline-flex rounded-full h-2 w-2 ${getStatusColor()}`}></span>
        </span>
        <span className="hidden sm:inline">{getStatusText()}</span>
      </button>

      {/* Details Dropdown */}
      {showDetails && (
        <>
          {/* Overlay to close dropdown */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowDetails(false)}
          />
          
          {/* Dropdown Content */}
          <div className="absolute right-0 mt-2 w-72 bg-gray-800 rounded-lg shadow-xl border border-gray-700 z-20 overflow-hidden">
            {/* Header */}
            <div className={`px-4 py-3 border-b border-gray-700 ${isConnected ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
              <div className="flex items-center space-x-2">
                <span className="text-xl">{getStatusIcon()}</span>
                <div>
                  <h3 className="font-semibold text-white text-sm">WebSocket Status</h3>
                  <p className={`text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {getStatusText()}
                  </p>
                </div>
              </div>
            </div>

            {/* Details */}
            <div className="p-4 space-y-3">
              {isConnected && socket ? (
                <>
                  <DetailItem 
                    label="Client ID" 
                    value={socket.id || 'N/A'} 
                  />
                  <DetailItem 
                    label="Transport" 
                    value={socket.io.engine.transport.name || 'N/A'} 
                  />
                  <DetailItem 
                    label="Server" 
                    value="http://localhost:5000" 
                  />
                  <div className="pt-2 border-t border-gray-700">
                    <p className="text-xs text-gray-400">
                      Real-time updates active
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="text-center py-4">
                    <p className="text-sm text-gray-400 mb-2">
                      Connection lost
                    </p>
                    <p className="text-xs text-gray-500">
                      Attempting to reconnect...
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      window.location.reload();
                    }}
                    className="w-full px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                  >
                    Reload Page
                  </button>
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 bg-gray-900 border-t border-gray-700">
              <p className="text-xs text-gray-500 text-center">
                WebSocket Protocol • Real-time Communication
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

interface DetailItemProps {
  label: string;
  value: string;
}

const DetailItem: React.FC<DetailItemProps> = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-xs text-gray-400">{label}:</span>
    <span className="text-xs text-white font-mono bg-gray-900 px-2 py-1 rounded">
      {value}
    </span>
  </div>
);

export default WebSocketStatus;

