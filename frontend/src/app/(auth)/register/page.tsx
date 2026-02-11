'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { UserCircle, GraduationCap, Users, ArrowRight, Loader2 } from 'lucide-react'
import { OTPInput } from '@/components/auth/OTPInput'
import { useAuth } from '@/lib/hooks/useAuth'
import { cn } from '@/lib/utils'

function RegisterContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { sendOTP, verifyOTP, register } = useAuth()

  const [step, setStep] = useState<'phone' | 'otp' | 'type' | 'details'>('phone')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [idToken, setIdToken] = useState<string | null>(null)
  const [userType, setUserType] = useState<'student' | 'parent' | null>(null)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [grade, setGrade] = useState<number>(5)
  const [isLoading, setIsLoading] = useState(false)

  // Check if token is passed from login page
  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      setIdToken(token)
      setStep('type')
    }
  }, [searchParams])

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()

    if (phoneNumber.length < 10) {
      alert('Please enter a valid phone number')
      return
    }

    setIsLoading(true)

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

    const token = await verifyOTP(otp)

    if (token) {
      setIdToken(token)
      setStep('type')
    }

    setIsLoading(false)
  }

  const handleSelectType = (type: 'student' | 'parent') => {
    setUserType(type)
    setStep('details')
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!idToken || !userType) return

    if (!name) {
      alert('Please enter your name')
      return
    }

    if (userType === 'student' && !grade) {
      alert('Please select your grade')
      return
    }

    setIsLoading(true)

    await register({
      id_token: idToken,
      user_type: userType,
      name,
      grade: userType === 'student' ? grade : undefined,
      email: email || undefined,
    })

    setIsLoading(false)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
          <p className="mt-2 text-gray-600">Join EduPilot AI to start learning</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl bg-white p-8 shadow-xl">
          {step === 'phone' && (
            <>
              <form onSubmit={handleSendOTP} className="space-y-6">
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <input
                    id="phone"
                    type="tel"
                    placeholder="Enter your phone number"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="mt-2 block w-full rounded-lg border border-gray-300 px-3 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    disabled={isLoading}
                    autoFocus
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Enter 10-digit mobile number
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={isLoading || phoneNumber.length < 10}
                  className={cn(
                    'flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 font-medium text-white',
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

              <div id="recaptcha-container"></div>

              <div className="mt-6 text-center text-sm text-gray-600">
                Already have an account?{' '}
                <Link href="/login" className="font-medium text-blue-600 hover:text-blue-700">
                  Login here
                </Link>
              </div>
            </>
          )}

          {step === 'otp' && (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-900">Enter OTP</h2>
                <p className="mt-2 text-sm text-gray-600">We sent a code to {phoneNumber}</p>
              </div>

              <OTPInput onComplete={handleVerifyOTP} disabled={isLoading} />

              {isLoading && (
                <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Verifying...
                </div>
              )}
            </div>
          )}

          {step === 'type' && (
            <div className="space-y-6">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-900">I am a...</h2>
                <p className="mt-2 text-sm text-gray-600">Select your account type</p>
              </div>

              <div className="grid gap-4">
                <button
                  onClick={() => handleSelectType('student')}
                  className="group relative flex items-center gap-4 rounded-lg border-2 border-gray-200 p-6 transition hover:border-blue-500 hover:bg-blue-50"
                >
                  <div className="rounded-full bg-blue-100 p-3 group-hover:bg-blue-200">
                    <GraduationCap className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="flex-1 text-left">
                    <h3 className="font-semibold text-gray-900">Student</h3>
                    <p className="text-sm text-gray-600">I want to learn and practice</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600" />
                </button>

                <button
                  onClick={() => handleSelectType('parent')}
                  className="group relative flex items-center gap-4 rounded-lg border-2 border-gray-200 p-6 transition hover:border-green-500 hover:bg-green-50"
                >
                  <div className="rounded-full bg-green-100 p-3 group-hover:bg-green-200">
                    <Users className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="flex-1 text-left">
                    <h3 className="font-semibold text-gray-900">Parent</h3>
                    <p className="text-sm text-gray-600">I want to track my child's progress</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-green-600" />
                </button>
              </div>
            </div>
          )}

          {step === 'details' && (
            <form onSubmit={handleRegister} className="space-y-6">
              <div className="text-center">
                <UserCircle className="mx-auto h-16 w-16 text-blue-600" />
                <h2 className="mt-4 text-xl font-semibold text-gray-900">Your Details</h2>
                <p className="mt-2 text-sm text-gray-600">
                  {userType === 'student' ? 'Student Information' : 'Parent Information'}
                </p>
              </div>

              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Full Name *
                </label>
                <input
                  id="name"
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-2 block w-full rounded-lg border border-gray-300 px-3 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  required
                />
              </div>

              {userType === 'student' && (
                <div>
                  <label htmlFor="grade" className="block text-sm font-medium text-gray-700">
                    Grade *
                  </label>
                  <select
                    id="grade"
                    value={grade}
                    onChange={(e) => setGrade(Number(e.target.value))}
                    className="mt-2 block w-full rounded-lg border border-gray-300 px-3 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    required
                  >
                    {[3, 4, 5, 6, 7, 8, 9, 10].map((g) => (
                      <option key={g} value={g}>
                        Grade {g}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email (Optional)
                </label>
                <input
                  id="email"
                  type="email"
                  placeholder="your.email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-2 block w-full rounded-lg border border-gray-300 px-3 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !name}
                className={cn(
                  'flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 font-medium text-white',
                  isLoading || !name
                    ? 'cursor-not-allowed bg-gray-400'
                    : 'bg-blue-600 hover:bg-blue-700'
                )}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Creating Account...
                  </>
                ) : (
                  <>
                    Complete Registration
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        <div className="mt-6 text-center">
          <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <RegisterContent />
    </Suspense>
  )
}
