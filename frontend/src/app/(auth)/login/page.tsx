'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Phone, ArrowRight, Loader2 } from 'lucide-react'
import { OTPInput } from '@/components/auth/OTPInput'
import { useAuth } from '@/lib/hooks/useAuth'
import { cn } from '@/lib/utils'

export default function LoginPage() {
  const router = useRouter()
  const { sendOTP, verifyOTP, login } = useAuth()

  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()

    if (phoneNumber.length < 10) {
      alert('Please enter a valid phone number')
      return
    }

    setIsLoading(true)

    // Format phone number with country code
    const formattedPhone = phoneNumber.startsWith('+')
      ? phoneNumber
      : phoneNumber.startsWith('91')
      ? '+' + phoneNumber
      : '+91' + phoneNumber

    const success = await sendOTP(formattedPhone)

    setIsLoading(false)

    if (success) {
      setStep('otp')
    }
  }

  const handleVerifyOTP = async (otp: string) => {
    setIsLoading(true)

    const idToken = await verifyOTP(otp)

    if (idToken) {
      const result = await login(idToken)

      // If user not found, redirect to registration with token
      if (result === 'not_found') {
        router.push(`/register?token=${encodeURIComponent(idToken)}`)
      }
    }

    setIsLoading(false)
  }

  const handleResendOTP = async () => {
    const formattedPhone = phoneNumber.startsWith('+')
      ? phoneNumber
      : phoneNumber.startsWith('91')
      ? '+' + phoneNumber
      : '+91' + phoneNumber

    await sendOTP(formattedPhone)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
          <p className="mt-2 text-gray-600">Sign in to continue learning</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl bg-white p-8 shadow-xl">
          {step === 'phone' ? (
            <>
              <form onSubmit={handleSendOTP} className="space-y-6">
                {/* Phone Number Input */}
                <div>
                  <label
                    htmlFor="phone"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Phone Number
                  </label>
                  <div className="relative mt-2">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                      <Phone className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="phone"
                      type="tel"
                      placeholder="Enter your phone number"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      className="block w-full rounded-lg border border-gray-300 py-3 pl-10 pr-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                      disabled={isLoading}
                      autoFocus
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Enter 10-digit mobile number (e.g., 9876543210)
                  </p>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading || phoneNumber.length < 10}
                  className={cn(
                    'flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 font-medium text-white',
                    'focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2',
                    isLoading || phoneNumber.length < 10
                      ? 'cursor-not-allowed bg-gray-400'
                      : 'bg-blue-600 hover:bg-blue-700'
                  )}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Sending OTP...
                    </>
                  ) : (
                    <>
                      Continue
                      <ArrowRight className="h-5 w-5" />
                    </>
                  )}
                </button>
              </form>

              {/* reCAPTCHA container */}
              <div id="recaptcha-container"></div>

              {/* Register Link */}
              <div className="mt-6 text-center text-sm text-gray-600">
                Don&apos;t have an account?{' '}
                <Link href="/register" className="font-medium text-blue-600 hover:text-blue-700">
                  Register here
                </Link>
              </div>
            </>
          ) : (
            <>
              {/* OTP Verification */}
              <div className="space-y-6">
                <div className="text-center">
                  <h2 className="text-xl font-semibold text-gray-900">Enter OTP</h2>
                  <p className="mt-2 text-sm text-gray-600">
                    We sent a code to {phoneNumber}
                  </p>
                </div>

                <OTPInput onComplete={handleVerifyOTP} disabled={isLoading} />

                {isLoading && (
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Verifying...
                  </div>
                )}

                {/* Resend OTP */}
                <div className="text-center">
                  <button
                    onClick={handleResendOTP}
                    disabled={isLoading}
                    className="text-sm font-medium text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                  >
                    Resend OTP
                  </button>
                </div>

                {/* Back Button */}
                <button
                  onClick={() => setStep('phone')}
                  disabled={isLoading}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:bg-gray-100"
                >
                  Change Phone Number
                </button>
              </div>
            </>
          )}
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
