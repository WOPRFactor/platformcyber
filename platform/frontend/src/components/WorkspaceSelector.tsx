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
  const statusText = status === 'active' ? 'Active' : status === 'archived' ? 'Archived' : 'Paused';
  
  const formatLogCount = (count: number) => {
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-600/30 text-slate-400">
          {statusText}
        </span>
        <span className="text-slate-500">Loading...</span>
      </div>
    );
  }

  const logCount = stats?.total_logs || 0;
  const logText = logCount === 0 ? 'No logs' : `${formatLogCount(logCount)} logs`;

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
        status === 'active' 
          ? 'bg-emerald-500/20 text-emerald-400' 
          : status === 'archived'
          ? 'bg-slate-500/20 text-slate-400'
          : 'bg-amber-500/20 text-amber-400'
      }`}>
        {statusText}
      </span>
      <span className="text-slate-500">{logText}</span>
      {stats && stats.size_mb > 10 && (
        <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px] font-semibold">
          {stats.size_mb.toFixed(1)}MB
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
    toast.success(`Workspace changed: ${workspace.name}`);
  };

  const handleCreateWorkspace = async (data: any) => {
    const workspace = await createWorkspace(data);
    selectWorkspace(workspace.id);
    setIsOpen(false);
    setSearchQuery('');
    return;
  };

  const handleDeleteWorkspace = async (workspaceId: number, workspaceName: string) => {
    if (!confirm(`Are you sure you want to delete workspace "${workspaceName}"?\n\nThis action is permanent and will delete:\n- The workspace and all its data\n- All scans and results\n- The complete filesystem directory\n\nThis action CANNOT be undone.`)) {
      return;
    }

    setIsDeleting(true);
    setWorkspaceToDelete(workspaceId);
    try {
      await deleteWorkspace(workspaceId);
      toast.success(`Workspace "${workspaceName}" deleted successfully`);
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      if (currentWorkspace?.id === workspaceId) {
        await new Promise(resolve => setTimeout(resolve, 200));
        const updatedWorkspaces = workspaces.filter(w => w.id !== workspaceId);
        if (updatedWorkspaces.length > 0) {
          selectWorkspace(updatedWorkspaces[0].id);
        }
      }
      
      setIsOpen(false);
      setSearchQuery('');
    } catch (error: any) {
      toast.error(error?.response?.data?.message || `Error deleting workspace: ${error.message}`);
    } finally {
      setIsDeleting(false);
      setWorkspaceToDelete(null);
    }
  };

  if (isLoadingWorkspaces) {
    return (
      <div className={`${className} flex items-center gap-2 px-3 py-2 bg-white/5 rounded-xl`}>
        <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-slate-400 text-sm">Loading...</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Selector principal */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-3 py-2 bg-white/5 hover:bg-white/10 rounded-xl transition-all duration-200 group w-full"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Briefcase className="w-4 h-4 text-slate-400 flex-shrink-0" />
          <div className="flex-1 min-w-0 text-left">
            <div className="text-sm font-medium text-white truncate">
              {currentWorkspace?.name || 'Select Workspace'}
            </div>
            {currentWorkspace?.client_name && (
              <div className="text-xs text-slate-500 truncate">
                {currentWorkspace.client_name}
              </div>
            )}
          </div>
        </div>
        <ChevronDown 
          className={`w-4 h-4 text-slate-500 transition-all duration-200 flex-shrink-0 ${
            isOpen ? 'rotate-180 text-white' : ''
          }`} 
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-[320px] bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-[9999] overflow-hidden">
          {/* Header con búsqueda */}
          <div className="p-3 border-b border-slate-700/50">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search workspace..."
                className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 transition-all"
              />
            </div>
          </div>

          {/* Lista de workspaces */}
          <div className="max-h-[350px] overflow-y-auto sidebar-scrollbar">
            {filteredWorkspaces.length === 0 ? (
              <div className="p-6 text-center">
                <Briefcase className="w-10 h-10 text-slate-700 mx-auto mb-3" />
                <p className="text-slate-500 text-sm">
                  {searchQuery ? 'No workspaces found' : 'No workspaces available'}
                </p>
              </div>
            ) : (
              filteredWorkspaces.map((workspace) => {
                const isActive = currentWorkspace?.id === workspace.id;
                return (
                  <div
                    key={workspace.id}
                    className={`transition-all duration-150 hover:bg-slate-800/70 ${
                      isActive 
                        ? 'bg-red-500/10 border-l-2 border-red-500' 
                        : 'border-l-2 border-transparent hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 px-4 py-3">
                      <button
                        onClick={() => handleWorkspaceSelect(workspace)}
                        className="flex-1 min-w-0 text-left"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Briefcase className={`w-4 h-4 flex-shrink-0 ${
                              isActive ? 'text-red-400' : 'text-slate-500'
                            } transition-colors`} />
                            <span className={`text-sm font-medium truncate ${
                              isActive ? 'text-white' : 'text-slate-200'
                            }`}>
                              {workspace.name}
                            </span>
                            {isActive && (
                              <Check className="w-4 h-4 text-red-400 flex-shrink-0" />
                            )}
                          </div>

                          <div className="ml-6 space-y-1">
                            {workspace.client_name && (
                              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                                <Users className="w-3 h-3" />
                                <span className="truncate">{workspace.client_name}</span>
                              </div>
                            )}
                            {workspace.target_domain && (
                              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                                <Globe className="w-3 h-3" />
                                <span className="truncate">{workspace.target_domain}</span>
                              </div>
                            )}
                            <WorkspaceLogsIndicatorCompact workspace={workspace} />
                          </div>
                        </div>
                      </button>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        {isActive && (
                          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        )}
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteWorkspace(workspace.id, workspace.name);
                          }}
                          disabled={isDeleting && workspaceToDelete === workspace.id}
                          className={`opacity-40 hover:opacity-100 transition-all p-1.5 rounded hover:bg-red-500/20 hover:text-red-400 text-slate-500 ${
                            isDeleting && workspaceToDelete === workspace.id ? 'opacity-100 animate-pulse bg-red-500/20 text-red-400' : ''
                          }`}
                          title="Delete workspace"
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
          <div className="border-t border-slate-700/50"></div>

          {/* Botones de acción */}
          <div className="p-3 space-y-2">
            {currentWorkspace && (
              <button
                onClick={() => {
                  setShowFilesConsole(true);
                  setIsOpen(false);
                }}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 rounded-xl transition-all duration-200"
              >
                <FolderOpen className="w-4 h-4 text-slate-400" />
                <span className="text-sm font-medium text-slate-300">View Files</span>
              </button>
            )}
            <button
              onClick={() => {
                setShowModal(true);
                setIsOpen(false);
                setSearchQuery('');
              }}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 hover:bg-red-700 rounded-xl transition-all duration-200"
            >
              <Plus className="w-4 h-4 text-white" />
              <span className="text-sm font-medium text-white">New Workspace</span>
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
