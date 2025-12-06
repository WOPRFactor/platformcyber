import React, { useState, useRef, useEffect } from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { ChevronDown, Plus, Settings, Users, Globe, Check, Briefcase, Search, Trash2, FolderOpen } from 'lucide-react';
import { toast } from 'sonner';
import WorkspaceFormModal from './WorkspaceFormModal';
import { WorkspaceFilesConsole } from './WorkspaceFilesConsole';
import { useQuery } from '@tanstack/react-query';
import { workspacesAPI } from '../lib/api/workspaces/workspaces';

interface WorkspaceSelectorProps {
  className?: string;
}

/**
 * Componente compacto para mostrar logs de workspace en el selector
 */
const WorkspaceLogsIndicatorCompact: React.FC<{ workspace: any }> = ({ workspace }) => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['workspace-logs-stats', workspace.id],
    queryFn: () => workspacesAPI.getWorkspaceLogsStats(workspace.id),
    enabled: !!workspace.id,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false
  });

  const status = workspace.status || (workspace.is_active ? 'active' : 'archived');
  const statusText = status === 'active' ? 'Activo' : status === 'archived' ? 'Archivado' : 'Pausado';
  
  const formatLogCount = (count: number) => {
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-500/20 text-gray-400">
          {statusText}
        </span>
        <span className="text-gray-500">Cargando...</span>
      </div>
    );
  }

  const logCount = stats?.total_logs || 0;
  const logText = logCount === 0 ? 'Sin logs' : `${formatLogCount(logCount)} logs`;

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
        status === 'active' 
          ? 'bg-green-500/20 text-green-400' 
          : status === 'archived'
          ? 'bg-gray-500/20 text-gray-400'
          : 'bg-yellow-500/20 text-yellow-400'
      }`}>
        {statusText}
      </span>
      <span className="text-gray-500">{logText}</span>
      {stats && stats.size_mb > 10 && (
        <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px] font-semibold">
          ⚠️ {stats.size_mb.toFixed(1)}MB
        </span>
      )}
    </div>
  );
};

export const WorkspaceSelector: React.FC<WorkspaceSelectorProps> = ({ className = '' }) => {
  const {
    currentWorkspace,
    workspaces,
    selectWorkspace,
    createWorkspace,
    deleteWorkspace,
    isLoadingWorkspaces
  } = useWorkspace();

  const [isOpen, setIsOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showFilesConsole, setShowFilesConsole] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [workspaceToDelete, setWorkspaceToDelete] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      // Focus en el input de búsqueda cuando se abre
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 100);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Filtrar workspaces por búsqueda
  const filteredWorkspaces = workspaces.filter(workspace =>
    workspace.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    workspace.client_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    workspace.target_domain?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleWorkspaceSelect = (workspace: any) => {
    selectWorkspace(workspace.id);
    setIsOpen(false);
    setSearchQuery('');
    toast.success(`Workspace cambiado: ${workspace.name}`);
  };

  const handleCreateWorkspace = async (data: any) => {
    const workspace = await createWorkspace(data);
    selectWorkspace(workspace.id);
    setIsOpen(false);
    setSearchQuery('');
    return;
  };

  const handleDeleteWorkspace = async (workspaceId: number, workspaceName: string) => {
    if (!confirm(`¿Estás seguro de que deseas eliminar el workspace "${workspaceName}"?\n\nEsta acción es permanente y eliminará:\n- El workspace y todos sus datos\n- Todos los escaneos y resultados\n- El directorio completo del filesystem\n\nEsta acción NO se puede deshacer.`)) {
      return;
    }

    setIsDeleting(true);
    setWorkspaceToDelete(workspaceId);
    try {
      await deleteWorkspace(workspaceId);
      toast.success(`Workspace "${workspaceName}" eliminado exitosamente`);
      
      // Esperar un momento para que la query se actualice
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Si el workspace eliminado era el actual, seleccionar el primero disponible
      // La lista ya debería estar actualizada por el refetch en el contexto
      if (currentWorkspace?.id === workspaceId) {
        // Esperar un poco más para que la lista se actualice completamente
        await new Promise(resolve => setTimeout(resolve, 200));
        // Obtener la lista actualizada del contexto
        const updatedWorkspaces = workspaces.filter(w => w.id !== workspaceId);
        if (updatedWorkspaces.length > 0) {
          selectWorkspace(updatedWorkspaces[0].id);
        }
      }
      
      setIsOpen(false);
      setSearchQuery('');
    } catch (error: any) {
      toast.error(error?.response?.data?.message || `Error al eliminar workspace: ${error.message}`);
    } finally {
      setIsDeleting(false);
      setWorkspaceToDelete(null);
    }
  };

  if (isLoadingWorkspaces) {
    return (
      <div className={`${className} flex items-center space-x-2 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg`}>
        <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-gray-400 text-sm">Cargando...</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Selector principal - Mejorado */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-4 py-2.5 bg-gray-800/80 backdrop-blur-sm border border-gray-700 hover:border-green-500/50 hover:bg-gray-750 rounded-lg transition-all duration-200 group min-w-[200px] max-w-[280px]"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Briefcase className="w-4 h-4 text-green-400 flex-shrink-0" />
          <div className="flex-1 min-w-0 text-left">
            <div className="text-sm font-semibold text-white truncate">
              {currentWorkspace?.name || 'Seleccionar Workspace'}
            </div>
            {currentWorkspace?.client_name && (
              <div className="text-xs text-gray-400 truncate">
                {currentWorkspace.client_name}
              </div>
            )}
          </div>
        </div>
        <ChevronDown 
          className={`w-4 h-4 text-gray-400 transition-all duration-200 flex-shrink-0 group-hover:text-green-400 ${
            isOpen ? 'rotate-180 text-green-400' : ''
          }`} 
        />
      </button>

      {/* Dropdown mejorado */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-[380px] bg-gray-900/95 backdrop-blur-md border border-gray-700 rounded-xl shadow-2xl z-[9999] overflow-hidden">
          {/* Header del dropdown con búsqueda */}
          <div className="p-3 border-b border-gray-700 bg-gray-800/50">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar workspace..."
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
              />
            </div>
          </div>

          {/* Lista de workspaces */}
          <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
            {filteredWorkspaces.length === 0 ? (
              <div className="p-6 text-center">
                <Briefcase className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400 text-sm">
                  {searchQuery ? 'No se encontraron workspaces' : 'No hay workspaces disponibles'}
                </p>
              </div>
            ) : (
              filteredWorkspaces.map((workspace) => {
                const isActive = currentWorkspace?.id === workspace.id;
                return (
                  <div
                    key={workspace.id}
                    className={`w-full transition-all duration-150 hover:bg-gray-800/70 group ${
                      isActive 
                        ? 'bg-green-500/10 border-l-4 border-green-500' 
                        : 'border-l-4 border-transparent hover:border-l-4 hover:border-green-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 px-4 py-3">
                      <button
                        onClick={() => handleWorkspaceSelect(workspace)}
                        className="flex-1 min-w-0 text-left"
                      >
                        <div className="flex-1 min-w-0">
                          {/* Nombre del workspace */}
                          <div className="flex items-center gap-2 mb-1">
                            <Briefcase className={`w-4 h-4 flex-shrink-0 ${
                              isActive ? 'text-green-400' : 'text-gray-500 group-hover:text-green-400'
                            } transition-colors`} />
                            <span className={`text-sm font-semibold truncate ${
                              isActive ? 'text-green-400' : 'text-white'
                            }`}>
                              {workspace.name}
                            </span>
                            {isActive && (
                              <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                            )}
                          </div>

                          {/* Información adicional */}
                          <div className="ml-6 space-y-1">
                            {workspace.client_name && (
                              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                                <Users className="w-3 h-3" />
                                <span className="truncate">{workspace.client_name}</span>
                              </div>
                            )}
                            {workspace.target_domain && (
                              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                                <Globe className="w-3 h-3" />
                                <span className="truncate">{workspace.target_domain}</span>
                              </div>
                            )}
                            {/* Estado y logs - versión compacta */}
                            <WorkspaceLogsIndicatorCompact workspace={workspace} />
                          </div>
                        </div>
                      </button>

                      {/* Botón de eliminar - siempre visible */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {/* Indicador visual de activo */}
                        {isActive && (
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        )}
                        
                        {/* Botón de eliminar */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteWorkspace(workspace.id, workspace.name);
                          }}
                          disabled={isDeleting && workspaceToDelete === workspace.id}
                          className={`opacity-40 hover:opacity-100 transition-all p-1.5 rounded hover:bg-red-500/20 hover:text-red-400 text-gray-400 ${
                            isDeleting && workspaceToDelete === workspace.id ? 'opacity-100 animate-pulse bg-red-500/20 text-red-400' : ''
                          }`}
                          title="Eliminar workspace"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Separador */}
          <div className="border-t border-gray-700"></div>

          {/* Botones de acción */}
          <div className="p-3 bg-gray-800/30 space-y-2">
            {currentWorkspace && (
              <button
                onClick={() => {
                  setShowFilesConsole(true);
                  setIsOpen(false);
                }}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/50 hover:border-blue-500 rounded-lg transition-all duration-200 group"
              >
                <FolderOpen className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
                <span className="text-sm font-medium text-blue-400">Ver Archivos</span>
              </button>
            )}
            <button
              onClick={() => {
                setShowModal(true);
                setIsOpen(false);
                setSearchQuery('');
              }}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600/20 hover:bg-green-600/30 border border-green-500/50 hover:border-green-500 rounded-lg transition-all duration-200 group"
            >
              <Plus className="w-4 h-4 text-green-400 group-hover:scale-110 transition-transform" />
              <span className="text-sm font-medium text-green-400">Crear Nuevo Workspace</span>
            </button>
          </div>
        </div>
      )}

      {/* Modal de creación de workspace */}
      <WorkspaceFormModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSubmit={handleCreateWorkspace}
        mode="create"
      />

      {/* Consola de archivos del workspace */}
      <WorkspaceFilesConsole
        isOpen={showFilesConsole}
        onClose={() => setShowFilesConsole(false)}
      />
    </div>
  );
};
