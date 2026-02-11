/**
 * Authentication state management with Zustand
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, Student, Parent } from '@/types'

interface AuthState {
  // State
  user: User | null
  student: Student | null
  parent: Parent | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  setAuth: (data: {
    user: User
    student?: Student
    parent?: Parent
    accessToken: string
  }) => void
  clearAuth: () => void
  setLoading: (loading: boolean) => void
  updateUser: (user: User) => void
  updateStudent: (student: Student) => void
  updateParent: (parent: Parent) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      student: null,
      parent: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,

      // Set authentication data
      setAuth: (data) => {
        // Store token in localStorage
        if (data.accessToken) {
          localStorage.setItem('access_token', data.accessToken)
        }

        set({
          user: data.user,
          student: data.student || null,
          parent: data.parent || null,
          accessToken: data.accessToken,
          isAuthenticated: true,
          isLoading: false,
        })
      },

      // Clear authentication data
      clearAuth: () => {
        localStorage.removeItem('access_token')

        set({
          user: null,
          student: null,
          parent: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      // Set loading state
      setLoading: (loading) => set({ isLoading: loading }),

      // Update user
      updateUser: (user) => set({ user }),

      // Update student
      updateStudent: (student) => set({ student }),

      // Update parent
      updateParent: (parent) => set({ parent }),
    }),
    {
      name: 'edupilot-auth-storage',
      partialize: (state) => ({
        user: state.user,
        student: state.student,
        parent: state.parent,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
