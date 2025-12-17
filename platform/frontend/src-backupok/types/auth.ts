/**
 * Authentication Types
 * ====================
 * 
 * Tipos relacionados con autenticación y usuarios.
 */

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  email_verified: boolean
  created_at: string
  last_login?: string
  role: string
  team?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: User
  expires_in: number
}

export interface LoginCredentials {
  username: string
  password: string
}


