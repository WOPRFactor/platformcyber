import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workspacesAPI } from '../lib/api/workspaces';
import { useConsole } from './ConsoleContext';

interface Workspace {
  id: number;
  name: string;
  schema_name?: string;
  description?: string;
  created_by?: number;
  owner_id?: number;
  
  // Cliente
  client_name?: string;
  client_contact?: string;
  
  // Target Principal
  target_domain?: string;
  target_ip?: string;
  target_type?: 'web' | 'api' | 'mobile' | 'network' | 'other';
  
  // Scope del Proyecto
  in_scope?: string;
  out_of_scope?: string;
  
  // Fechas del Proyecto
  start_date?: string | null;
  end_date?: string | null;
  
  // Notas
  notes?: string;
  
  // Configuración
  is_active?: boolean;
  settings?: Record<string, any>;
  member_count?: number;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

interface WorkspaceMember {
  id: number;
  user_id: number;
  workspace_id: number;
  role: 'owner' | 'collaborator' | 'viewer';
  joined_at: string;
  user: {
    id: number;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
}

interface Session {
  id: number;
  workspace_id: number;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'closed';
  created_by: number;
  created_at: string;
  updated_at: string;
  settings: Record<string, any>;
  evidence_count: number;
}

interface Evidence {
  id: number;
  workspace_id: number;
  session_id?: number;
  title: string;
  type: 'screen' | 'output' | 'file' | 'note' | 'command_log';
  content?: string;
  file_path?: string;
  metadata: Record<string, any>;
  tags: string[];
  created_by: number;
  created_at: string;
  updated_at: string;
  creator?: string;
}

interface WorkspaceContextType {
  // Estado actual
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  sessions: Session[];
  evidences: Evidence[];

  // Loading states
  isLoadingWorkspaces: boolean;
  isLoadingSessions: boolean;
  isLoadingEvidences: boolean;

  // Acciones
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  selectWorkspace: (workspaceId: number) => void;
  createWorkspace: (data: {
    name: string;
    description?: string;
    client_name?: string;
    client_contact?: string;
    target_domain?: string;
    target_ip?: string;
    target_type?: 'web' | 'api' | 'mobile' | 'network' | 'other';
    in_scope?: string;
    out_of_scope?: string;
    start_date?: string | null;
    end_date?: string | null;
    notes?: string;
    is_active?: boolean;
  }) => Promise<Workspace>;
  updateWorkspace: (id: number, data: Partial<Workspace>) => Promise<Workspace>;
  deleteWorkspace: (id: number) => Promise<void>;

  // Sesiones
  createSession: (workspaceId: number, data: { name: string; description?: string }) => Promise<Session>;
  getWorkspaceSessions: (workspaceId: number) => Promise<Session[]>;

  // Evidencias
  createEvidence: (workspaceId: number, data: {
    title: string;
    type: Evidence['type'];
    content?: string;
    session_id?: number;
    metadata?: Record<string, any>;
    tags?: string[];
  }) => Promise<Evidence>;
  getWorkspaceEvidences: (workspaceId: number, filters?: {
    session_id?: number;
    type?: string;
  }) => Promise<Evidence[]>;
  updateEvidence: (workspaceId: number, evidenceId: number, data: Partial<Evidence>) => Promise<Evidence>;
  deleteEvidence: (workspaceId: number, evidenceId: number) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
};

interface WorkspaceProviderProps {
  children: ReactNode;
}

export const WorkspaceProvider: React.FC<WorkspaceProviderProps> = ({ children }) => {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const queryClient = useQueryClient();

  // Ya no necesitamos resetear la consola al montar - los datos están aislados por workspace

  // Ya no necesitamos resetear la consola al cambiar de workspace - los datos están automáticamente aislados

  // Query para obtener workspaces - solo si está autenticado
  const { data: workspaces = [], isLoading: isLoadingWorkspaces } = useQuery({
    queryKey: ['workspaces'],
    queryFn: async () => {
      return await workspacesAPI.getWorkspaces();
    },
    enabled: !!localStorage.getItem('access_token'), // Solo ejecutar si hay token
    staleTime: 0, // Siempre considerar datos stale para forzar refetch después de mutaciones
    refetchOnWindowFocus: true, // Refetch cuando la ventana recupera el foco
  });

  // Query para obtener sesiones del workspace actual
  const { data: sessions = [], isLoading: isLoadingSessions } = useQuery({
    queryKey: ['sessions', currentWorkspace?.id],
    queryFn: async () => {
      if (!currentWorkspace) return [];
      return await workspacesAPI.getWorkspaceSessions(currentWorkspace.id);
    },
    enabled: !!currentWorkspace && !!localStorage.getItem('access_token'), // Solo si hay workspace y token
    staleTime: 2 * 60 * 1000, // 2 minutos
  });

  // Query para obtener evidencias del workspace actual
  const { data: evidences = [], isLoading: isLoadingEvidences } = useQuery({
    queryKey: ['evidences', currentWorkspace?.id],
    queryFn: async () => {
      if (!currentWorkspace) return [];
      return await workspacesAPI.getWorkspaceEvidence(currentWorkspace.id);
    },
    enabled: !!currentWorkspace,
    staleTime: 1 * 60 * 1000, // 1 minuto
  });

  // Mutations
  const createWorkspaceMutation = useMutation({
    mutationFn: async (data: Parameters<WorkspaceContextType['createWorkspace']>[0]) => {
      return await workspacesAPI.createWorkspace(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
    },
  });

  const updateWorkspaceMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<Workspace> }) => {
      return await workspacesAPI.updateWorkspace(id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] });
    },
  });

  const deleteWorkspaceMutation = useMutation({
    mutationFn: async (id: number) => {
      await workspacesAPI.deleteWorkspace(id);
    },
    onSuccess: async (_, id) => {
      // Invalidar y refetch inmediatamente para actualizar la lista
      await queryClient.invalidateQueries({ queryKey: ['workspaces'] });
      await queryClient.refetchQueries({ queryKey: ['workspaces'] });
      
      // Si el workspace eliminado era el actual, limpiar selección
      if (currentWorkspace?.id === id) {
        setCurrentWorkspace(null);
      }
    },
  });

  const createSessionMutation = useMutation({
    mutationFn: async ({ workspaceId, data }: {
      workspaceId: number;
      data: { name: string; description?: string }
    }) => {
      return await workspacesAPI.createSession(workspaceId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
  });

  const createEvidenceMutation = useMutation({
    mutationFn: async ({ workspaceId, data }: {
      workspaceId: number;
      data: Parameters<WorkspaceContextType['createEvidence']>[1]
    }) => {
      return await workspacesAPI.createEvidence(workspaceId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidences'] });
    },
  });

  const updateEvidenceMutation = useMutation({
    mutationFn: async ({ workspaceId, evidenceId, data }: {
      workspaceId: number;
      evidenceId: number;
      data: Partial<Evidence>
    }) => {
      return await workspacesAPI.updateEvidence(workspaceId, evidenceId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidences'] });
    },
  });

  const deleteEvidenceMutation = useMutation({
    mutationFn: async ({ workspaceId, evidenceId }: {
      workspaceId: number;
      evidenceId: number
    }) => {
      await workspacesAPI.deleteEvidence(workspaceId, evidenceId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidences'] });
    },
  });

  // Funciones públicas
  const createWorkspace = async (data: Parameters<WorkspaceContextType['createWorkspace']>[0]) => {
    return createWorkspaceMutation.mutateAsync(data);
  };

  const updateWorkspace = async (id: number, data: Partial<Workspace>) => {
    return updateWorkspaceMutation.mutateAsync({ id, data });
  };

  const deleteWorkspace = async (id: number) => {
    return deleteWorkspaceMutation.mutateAsync(id);
  };

  const createSession = async (workspaceId: number, data: { name: string; description?: string }) => {
    return createSessionMutation.mutateAsync({ workspaceId, data });
  };

  const getWorkspaceSessions = async (workspaceId: number) => {
    return await workspacesAPI.getWorkspaceSessions(workspaceId);
  };

  const createEvidence = async (workspaceId: number, data: Parameters<WorkspaceContextType['createEvidence']>[1]) => {
    return createEvidenceMutation.mutateAsync({ workspaceId, data });
  };

  const getWorkspaceEvidences = async (workspaceId: number, filters?: {
    session_id?: number;
    type?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.session_id) params.append('session_id', filters.session_id.toString());
    if (filters?.type) params.append('type', filters.type);

    return await workspacesAPI.getWorkspaceEvidence(workspaceId, filters);
  };

  const updateEvidence = async (workspaceId: number, evidenceId: number, data: Partial<Evidence>) => {
    return updateEvidenceMutation.mutateAsync({ workspaceId, evidenceId, data });
  };

  const deleteEvidence = async (workspaceId: number, evidenceId: number) => {
    return deleteEvidenceMutation.mutateAsync({ workspaceId, evidenceId });
  };

  // Función para seleccionar workspace
  const selectWorkspace = useCallback((workspaceId: number) => {
    const workspace = workspaces.find(w => w.id === workspaceId);
    if (workspace) {
      console.log(`🔄 Seleccionando workspace: ${workspace.name} - Cambiando contexto`);
      setCurrentWorkspace(workspace);
      // Limpiar cache de queries relacionadas con el workspace anterior
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      queryClient.invalidateQueries({ queryKey: ['evidences'] });
    }
  }, [workspaces, queryClient]);

  // Auto-seleccionar primer workspace si no hay ninguno seleccionado
  useEffect(() => {
    if (!currentWorkspace && workspaces.length > 0) {
      setCurrentWorkspace(workspaces[0]);
    }
  }, [workspaces, currentWorkspace]);

  const value: WorkspaceContextType = {
    // Estado
    currentWorkspace,
    workspaces,
    sessions,
    evidences,

    // Loading
    isLoadingWorkspaces,
    isLoadingSessions,
    isLoadingEvidences,

    // Acciones
    setCurrentWorkspace,
    selectWorkspace,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace,

    // Sesiones
    createSession,
    getWorkspaceSessions,

    // Evidencias
    createEvidence,
    getWorkspaceEvidences,
    updateEvidence,
    deleteEvidence,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
};
