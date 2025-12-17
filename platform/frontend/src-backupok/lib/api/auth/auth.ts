/**
 * Módulo de Autenticación
 * Maneja todas las operaciones relacionadas con autenticación de usuarios
 */

import { api } from '../shared/client'
import type {
  LoginCredentials,
  AuthResponse,
  User,
  ChangePasswordRequest,
  RefreshTokenResponse
} from './types'

/**
 * Realiza el login del usuario
 * @param credentials - Credenciales de login (username y password)
 * @returns Respuesta de autenticación con token y datos del usuario
 * @throws Error si las credenciales son inválidas
 */
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('auth/login', credentials)
  return response.data
}

/**
 * Realiza el logout del usuario actual
 * @returns Promise que se resuelve cuando el logout es exitoso
 */
export const logout = async (): Promise<void> => {
  await api.post('auth/logout')
}

/**
 * Refresca el token de acceso actual
 * @returns Nuevo token de acceso con tiempo de expiración
 * @throws Error si el refresh token es inválido
 */
export const refresh = async (): Promise<RefreshTokenResponse> => {
  const response = await api.post<RefreshTokenResponse>('auth/refresh')
  return response.data
}

/**
 * Obtiene los datos del usuario actualmente autenticado
 * @returns Datos del usuario actual
 * @throws Error si no hay usuario autenticado
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<{ user: User }>('auth/me')
  return response.data.user
}

/**
 * Cambia la contraseña del usuario actual
 * @param data - Contraseña actual y nueva contraseña
 * @returns Promise que se resuelve cuando el cambio es exitoso
 * @throws Error si la contraseña actual es incorrecta
 */
export const changePassword = async (data: ChangePasswordRequest): Promise<void> => {
  await api.post('auth/change-password', data)
}

/**
 * Objeto API de autenticación - compatible hacia atrás
 * Agrupa todas las funciones de autenticación
 */
export const authAPI = {
  login,
  logout,
  refresh,
  getCurrentUser,
  changePassword
}
