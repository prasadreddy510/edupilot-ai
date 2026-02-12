/**
 * Authentication API service
 */

import apiClient from './client'
import { AuthResponse } from '@/types'

export interface RegisterData {
  id_token: string
  user_type: 'student' | 'parent'
  name: string
  grade?: number
  email?: string
}

export interface LoginData {
  id_token: string
}

export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/api/v1/auth/register', data)
  },

  /**
   * Login existing user
   */
  login: async (data: LoginData): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/api/v1/auth/login', data)
  },

  /**
   * Get current user information
   */
  getCurrentUser: async (): Promise<AuthResponse> => {
    return apiClient.get<AuthResponse>('/api/v1/auth/me')
  },

  /**
   * Logout user
   */
  logout: async (): Promise<{ message: string }> => {
    return apiClient.post<{ message: string }>('/api/v1/auth/logout')
  },

  /**
   * Refresh access token
   */
  refreshToken: async (): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/api/v1/auth/refresh')
  },

  /**
   * Dev-only login (bypasses Firebase)
   */
  devLogin: async (): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/api/v1/auth/dev-login')
  },
}
