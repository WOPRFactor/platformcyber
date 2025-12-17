/**
 * Tipos relacionados con workspaces
 * Define las interfaces para workspaces, sesiones y evidencia
 */

export interface Workspace {
  id: number
  name: string
  schema_name?: string
  description?: string
  created_by?: number
  owner_id?: number
  
  // Cliente
  client_name?: string
  client_contact?: string
  
  // Target Principal
  target_domain?: string
  target_ip?: string
  target_type?: 'web' | 'api' | 'mobile' | 'network' | 'other'
  
  // Scope del Proyecto
  in_scope?: string
  out_of_scope?: string
  
  // Fechas del Proyecto
  start_date?: string | null
  end_date?: string | null
  
  // Notas
  notes?: string
  
  // Configuración
  is_active?: boolean
  status?: 'active' | 'paused' | 'archived' | 'completed'
  settings?: Record<string, unknown>
  member_count?: number
  
  // Timestamps
  created_at: string
  updated_at: string
}

export interface WorkspaceMember {
  id: number
  user_id: number
  workspace_id: number
  role: 'owner' | 'collaborator' | 'viewer'
  joined_at: string
  user: {
    id: number
    username: string
    email: string
    first_name?: string
    last_name?: string
  }
}

export interface Session {
  id: number
  workspace_id: number
  name: string
  description: string
  status: 'active' | 'paused' | 'closed'
  created_by: number
  created_at: string
  updated_at: string
  settings: Record<string, unknown>
  evidence_count: number
}

export interface Evidence {
  id: number
  workspace_id: number
  session_id?: number
  title: string
  description?: string
  type: 'image' | 'document' | 'log' | 'screenshot' | 'other'
  file_path: string
  file_size: number
  mime_type: string
  created_by: number
  created_at: string
  updated_at: string
  tags: string[]
}

export interface CreateWorkspaceData {
  name: string
  description?: string
  
  // Cliente
  client_name?: string
  client_contact?: string
  
  // Target Principal
  target_domain?: string
  target_ip?: string
  target_type?: 'web' | 'api' | 'mobile' | 'network' | 'other'
  
  // Scope del Proyecto
  in_scope?: string
  out_of_scope?: string
  
  // Fechas del Proyecto
  start_date?: string | null
  end_date?: string | null
  
  // Notas
  notes?: string
  
  // Configuración
  is_active?: boolean
}

export interface CreateSessionData {
  name: string
  description?: string
}

export interface CreateEvidenceData {
  title: string
  description?: string
  type: Evidence['type']
  file_path: string
  file_size: number
  mime_type: string
  tags?: string[]
}

export interface EvidenceFilters {
  type?: Evidence['type']
  session_id?: number
  tags?: string[]
}


