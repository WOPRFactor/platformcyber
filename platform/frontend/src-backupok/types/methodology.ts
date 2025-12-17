/**
 * Pentest Methodology Types
 * ==========================
 * 
 * Tipos relacionados con metodologías de pentesting y proyectos.
 */

export interface PentestMethodology {
  name: string
  description: string
  difficulty: 'baja' | 'media' | 'media-baja' | 'alta' | 'muy_alta'
  estimated_time: string
  scope: string
  access_level: string
  phases: string[]
  tools_recommended: string[]
  deliverables: string[]
}

export interface MethodologyWorkflow {
  methodology: string
  name: string
  description: string
  workflow_phases: WorkflowPhase[]
}

export interface WorkflowPhase {
  phase: string
  name: string
  description: string
  tools: string[]
  deliverables: string[]
  estimated_time: string
}

export interface PentestProject {
  id: string
  name: string
  methodology: string
  target: string
  scope: string[]
  client?: string
  start_date: string
  end_date?: string
  status: 'planning' | 'active' | 'paused' | 'completed' | 'cancelled'
  created_by: string
  team_members: string[]
  objectives: string[]
  rules_of_engagement: any
  methodology_details: PentestMethodology
  phases_completed: string[]
  findings: PentestFinding[]
  created_at: string
  updated_at: string
}

export interface PentestFinding {
  id: string
  title: string
  description: string
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical'
  category: string
  phase: string
  evidence: string[]
  remediation: string
  cvss_score?: number
  tags: string[]
  created_at: string
  created_by: string
}

export interface ProjectSummary {
  id: string
  name: string
  methodology: string
  target: string
  status: string
  start_date: string
  created_by: string
  phases_completed: number
}

export interface PentestDashboard {
  total_projects: number
  active_projects: number
  completed_projects: number
  methodology_distribution: Record<string, number>
  recent_projects: ProjectSummary[]
  projects_by_status: Record<string, number>
}

export interface CreateProjectData {
  name?: string
  methodology: string
  target: string
  scope?: string[]
  client?: string
  start_date?: string
  end_date?: string
  team_members?: string[]
  objectives?: string[]
  rules_of_engagement?: any
}


