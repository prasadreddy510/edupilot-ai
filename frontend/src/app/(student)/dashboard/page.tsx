'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api/client'
import { learningApi, LearningSessionStats } from '@/lib/api/learning'
import {
  BookOpen,
  Calculator,
  FlaskConical,
  Globe,
  Languages,
  Leaf,
  ArrowRight,
  Clock,
  Target,
  TrendingUp,
} from 'lucide-react'
import { Subject } from '@/types'

const SUBJECT_ICONS: { [key: string]: any } = {
  Mathematics: Calculator,
  Science: FlaskConical,
  'Social Science': Globe,
  English: BookOpen,
  Hindi: Languages,
  'Environmental Studies': Leaf,
}

const SUBJECT_COLORS: { [key: string]: string } = {
  Mathematics: 'bg-blue-100 text-blue-600 hover:bg-blue-200',
  Science: 'bg-green-100 text-green-600 hover:bg-green-200',
  'Social Science': 'bg-purple-100 text-purple-600 hover:bg-purple-200',
  English: 'bg-orange-100 text-orange-600 hover:bg-orange-200',
  Hindi: 'bg-pink-100 text-pink-600 hover:bg-pink-200',
  'Environmental Studies': 'bg-teal-100 text-teal-600 hover:bg-teal-200',
}

export default function StudentDashboard() {
  const router = useRouter()
  const { user, student, isAuthenticated } = useAuthStore()

  // Redirect if not authenticated or not a student
  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch subjects for student's grade
  const { data: subjects, isLoading } = useQuery<Subject[]>({
    queryKey: ['subjects', student?.grade],
    queryFn: async () => {
      return apiClient.get(`/api/v1/subjects?grade=${student?.grade}`)
    },
    enabled: !!student?.grade,
  })

  // Fetch learning stats
  const { data: learningStats } = useQuery<LearningSessionStats>({
    queryKey: ['learningStats'],
    queryFn: learningApi.getStats,
    enabled: !!student,
  })

  // Helper to format minutes into hours and minutes
  const formatMinutes = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) {
      return `${hours}h ${mins}m`
    }
    return `${mins}m`
  }

  if (!student) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome back, {student.name}! 👋
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Grade {student.grade} • Ready to learn today?
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/profile"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Profile
              </Link>
              <Link
                href="/progress"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Progress
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="mb-8 grid gap-6 md:grid-cols-3">
          <StatCard
            icon={<Clock className="h-6 w-6" />}
            title="Learning Time"
            value={learningStats ? formatMinutes(learningStats.time_this_week_minutes) : '0m'}
            subtitle="This week"
            color="blue"
          />
          <StatCard
            icon={<Target className="h-6 w-6" />}
            title="Topics Learned"
            value={learningStats?.unique_topics_learned.toString() || '0'}
            subtitle="Completed"
            color="green"
          />
          <StatCard
            icon={<TrendingUp className="h-6 w-6" />}
            title="Total Sessions"
            value={learningStats?.total_sessions.toString() || '0'}
            subtitle="All time"
            color="purple"
          />
        </div>

        {/* Subjects */}
        <section>
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Your Subjects</h2>
              <p className="mt-1 text-sm text-gray-600">
                Choose a subject to start learning
              </p>
            </div>
          </div>

          {isLoading ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div
                  key={i}
                  className="h-40 animate-pulse rounded-xl bg-gray-200"
                />
              ))}
            </div>
          ) : subjects && subjects.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {subjects.map((subject) => (
                <SubjectCard key={subject.id} subject={subject} />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900">
                No subjects available
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                Subjects for Grade {student.grade} will appear here.
              </p>
            </div>
          )}
        </section>

        {/* Quick Actions */}
        <section className="mt-12">
          <h2 className="mb-6 text-2xl font-bold text-gray-900">Quick Actions</h2>
          <div className="grid gap-6 md:grid-cols-2">
            <ActionCard
              href="/worksheets"
              icon="📝"
              title="Practice Worksheets"
              description="Generate AI-powered worksheets for any topic"
            />
            <ActionCard
              href="/quizzes"
              icon="🎯"
              title="Take a Quiz"
              description="Test your knowledge with timed quizzes"
            />
            <ActionCard
              href="/doubts"
              icon="💬"
              title="Ask a Doubt"
              description="Get instant help from AI tutor"
            />
            <ActionCard
              href="/progress"
              icon="📊"
              title="View Progress"
              description="See your learning journey and achievements"
            />
          </div>
        </section>
      </main>
    </div>
  )
}

function StatCard({
  icon,
  title,
  value,
  subtitle,
  color,
}: {
  icon: React.ReactNode
  title: string
  value: string
  subtitle: string
  color: 'blue' | 'green' | 'purple'
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">
      <div className="flex items-center gap-4">
        <div className={`rounded-lg p-3 ${colorClasses[color]}`}>{icon}</div>
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
      </div>
    </div>
  )
}

function SubjectCard({ subject }: { subject: Subject }) {
  const Icon = SUBJECT_ICONS[subject.name] || BookOpen
  const colorClass = SUBJECT_COLORS[subject.name] || 'bg-gray-100 text-gray-600'

  return (
    <Link
      href={`/subjects/${subject.id}`}
      className="group rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
    >
      <div className="flex items-start justify-between">
        <div className={`rounded-lg p-3 ${colorClass}`}>
          <Icon className="h-6 w-6" />
        </div>
        <ArrowRight className="h-5 w-5 text-gray-400 transition group-hover:translate-x-1 group-hover:text-gray-600" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-gray-900">{subject.name}</h3>
      <p className="mt-2 text-sm text-gray-600">
        {subject.description || `Grade ${subject.grade} ${subject.name}`}
      </p>
      <div className="mt-4 flex items-center gap-2 text-sm text-blue-600">
        <span>Start learning</span>
        <ArrowRight className="h-4 w-4" />
      </div>
    </Link>
  )
}

function ActionCard({
  href,
  icon,
  title,
  description,
}: {
  href: string
  icon: string
  title: string
  description: string
}) {
  return (
    <Link
      href={href}
      className="group rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
    >
      <div className="flex items-start gap-4">
        <div className="text-3xl">{icon}</div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <p className="mt-1 text-sm text-gray-600">{description}</p>
        </div>
        <ArrowRight className="h-5 w-5 text-gray-400 transition group-hover:translate-x-1 group-hover:text-gray-600" />
      </div>
    </Link>
  )
}
