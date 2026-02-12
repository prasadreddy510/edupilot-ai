'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useAuth } from '@/lib/hooks/useAuth'
import { cn, getGradeLabel } from '@/lib/utils'
import {
  ArrowLeft,
  User,
  Phone,
  Mail,
  GraduationCap,
  LogOut,
  Calendar,
} from 'lucide-react'

export default function ProfilePage() {
  const router = useRouter()
  const { user, student, isAuthenticated } = useAuthStore()
  const { logout } = useAuth()

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  if (!student || !user) return null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
              <p className="mt-1 text-sm text-gray-600">
                Manage your account
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Profile Card */}
        <div className="mx-auto max-w-2xl space-y-6">
          {/* Avatar & Name */}
          <div className="rounded-xl border border-gray-200 bg-white p-8 text-center">
            <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-blue-100">
              <User className="h-12 w-12 text-blue-600" />
            </div>
            <h2 className="mt-4 text-2xl font-bold text-gray-900">{student.name}</h2>
            <p className="mt-1 text-sm text-gray-500">{getGradeLabel(student.grade)}</p>
          </div>

          {/* Details */}
          <div className="rounded-xl border border-gray-200 bg-white divide-y">
            <ProfileRow
              icon={<Phone className="h-5 w-5 text-gray-400" />}
              label="Phone Number"
              value={user.phone_number}
            />
            <ProfileRow
              icon={<Mail className="h-5 w-5 text-gray-400" />}
              label="Email"
              value={student.email || 'Not set'}
            />
            <ProfileRow
              icon={<GraduationCap className="h-5 w-5 text-gray-400" />}
              label="Grade"
              value={getGradeLabel(student.grade)}
            />
            <ProfileRow
              icon={<Calendar className="h-5 w-5 text-gray-400" />}
              label="Joined"
              value={new Date(user.created_at).toLocaleDateString('en-IN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            />
          </div>

          {/* Logout */}
          <button
            onClick={logout}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-4 text-red-600 hover:bg-red-50"
          >
            <LogOut className="h-5 w-5" />
            <span className="font-medium">Log Out</span>
          </button>
        </div>
      </main>
    </div>
  )
}

function ProfileRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-center gap-4 px-6 py-4">
      {icon}
      <div className="flex-1">
        <p className="text-sm text-gray-500">{label}</p>
        <p className="font-medium text-gray-900">{value}</p>
      </div>
    </div>
  )
}
