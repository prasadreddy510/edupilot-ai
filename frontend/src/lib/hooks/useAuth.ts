/**
 * Authentication hooks
 */

import { useState } from 'react'
import { toast } from 'sonner'
import {
  signInWithPhoneNumber,
  RecaptchaVerifier,
  ConfirmationResult,
} from 'firebase/auth'
import { auth } from '@/lib/firebase/config'
import { authApi, RegisterData } from '@/lib/api/auth'
import { useAuthStore } from '@/lib/store/authStore'
import { useRouter } from 'next/navigation'

export const useAuth = () => {
  const router = useRouter()
  const { setAuth, clearAuth, setLoading, isAuthenticated, user, student, parent } =
    useAuthStore()

  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(
    null
  )

  /**
   * Initialize reCAPTCHA verifier
   */
  const initializeRecaptcha = (elementId: string = 'recaptcha-container') => {
    if (typeof window === 'undefined') return null

    try {
      const recaptchaVerifier = new RecaptchaVerifier(auth, elementId, {
        size: 'invisible',
        callback: () => {
          console.log('reCAPTCHA solved')
        },
        'expired-callback': () => {
          toast.error('reCAPTCHA expired. Please try again.')
        },
      })

      return recaptchaVerifier
    } catch (error) {
      console.error('Error initializing reCAPTCHA:', error)
      toast.error('Failed to initialize reCAPTCHA')
      return null
    }
  }

  /**
   * Send OTP to phone number
   */
  const sendOTP = async (phoneNumber: string): Promise<boolean> => {
    try {
      setLoading(true)

      const recaptchaVerifier = initializeRecaptcha()
      if (!recaptchaVerifier) {
        throw new Error('Failed to initialize reCAPTCHA')
      }

      const result = await signInWithPhoneNumber(auth, phoneNumber, recaptchaVerifier)
      setConfirmationResult(result)

      toast.success('OTP sent successfully!')
      return true
    } catch (error: any) {
      console.error('Error sending OTP:', error)
      toast.error(error.message || 'Failed to send OTP')
      return false
    } finally {
      setLoading(false)
    }
  }

  /**
   * Verify OTP and get Firebase ID token
   */
  const verifyOTP = async (otp: string): Promise<string | null> => {
    try {
      if (!confirmationResult) {
        toast.error('Please send OTP first')
        return null
      }

      setLoading(true)

      const result = await confirmationResult.confirm(otp)
      const idToken = await result.user.getIdToken()

      return idToken
    } catch (error: any) {
      console.error('Error verifying OTP:', error)
      toast.error(error.message || 'Invalid OTP')
      return null
    } finally {
      setLoading(false)
    }
  }

  /**
   * Register new user
   */
  const register = async (data: RegisterData) => {
    try {
      setLoading(true)

      const response = await authApi.register(data)

      setAuth({
        user: response.user,
        student: response.student,
        parent: response.parent,
        accessToken: response.access_token,
      })

      toast.success('Registration successful!')

      // Redirect based on user type
      if (response.user.user_type === 'student') {
        router.push('/student/dashboard')
      } else {
        router.push('/parent/dashboard')
      }
    } catch (error: any) {
      console.error('Registration error:', error)
      toast.error(error.response?.data?.detail || 'Registration failed')
      throw error
    } finally {
      setLoading(false)
    }
  }

  /**
   * Login existing user
   */
  const login = async (idToken: string) => {
    try {
      setLoading(true)

      const response = await authApi.login({ id_token: idToken })

      setAuth({
        user: response.user,
        student: response.student,
        parent: response.parent,
        accessToken: response.access_token,
      })

      toast.success('Login successful!')

      // Redirect based on user type
      if (response.user.user_type === 'student') {
        router.push('/student/dashboard')
      } else {
        router.push('/parent/dashboard')
      }
    } catch (error: any) {
      console.error('Login error:', error)

      // If user not found, they need to register
      if (error.response?.status === 404) {
        toast.error('User not found. Please register first.')
        return 'not_found'
      }

      toast.error(error.response?.data?.detail || 'Login failed')
      throw error
    } finally {
      setLoading(false)
    }
  }

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      await authApi.logout()
      await auth.signOut()
      clearAuth()
      toast.success('Logged out successfully')
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
      // Clear local state even if API call fails
      clearAuth()
      router.push('/')
    }
  }

  /**
   * Get current user from API
   */
  const refreshUser = async () => {
    try {
      const response = await authApi.getCurrentUser()
      setAuth({
        user: response.user,
        student: response.student,
        parent: response.parent,
        accessToken: response.access_token || useAuthStore.getState().accessToken || '',
      })
    } catch (error) {
      console.error('Error refreshing user:', error)
      // If token is invalid, clear auth
      clearAuth()
    }
  }

  return {
    // State
    isAuthenticated,
    user,
    student,
    parent,

    // Actions
    sendOTP,
    verifyOTP,
    register,
    login,
    logout,
    refreshUser,
  }
}
