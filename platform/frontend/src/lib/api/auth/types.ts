/**
 * Tipos relacionados con autenticación
 * Define las interfaces y tipos para el sistema de autenticación
 */

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  last_login?: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface RefreshTokenResponse {
  access_token: string
  expires_in: number
}



