'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import {
  progressApi,
  StudentAnalytics,
  SubjectBreakdown,
  WeakArea,
  ProgressRecord,
} from '@/lib/api/progress'
import { cn, formatTime, getMasteryColor, getMasteryLabel, formatDate } from '@/lib/utils'
import {
  Clock,
  BookOpen,
  CheckCircle,
  TrendingUp,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Activity,
  Target,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

export default function ProgressDashboard() {
  const router = useRouter()
  const { student, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  const { data: analytics, isLoading: analyticsLoading } = useQuery<StudentAnalytics>({
    queryKey: ['progress', 'analytics'],
    queryFn: progressApi.getAnalytics,
    enabled: !!student,
  })

  const { data: subjects, isLoading: subjectsLoading } = useQuery<SubjectBreakdown[]>({
    queryKey: ['progress', 'subject-breakdown'],
    queryFn: progressApi.getSubjectBreakdown,
    enabled: !!student,
  })

  const { data: weakAreas, isLoading: weakAreasLoading } = useQuery<WeakArea[]>({
    queryKey: ['progress', 'weak-areas'],
    queryFn: () => progressApi.getWeakAreas(5),
    enabled: !!student,
  })

  const { data: records, isLoading: recordsLoading } = useQuery<ProgressRecord[]>({
    queryKey: ['progress', 'records'],
    queryFn: () => progressApi.getRecords(),
    enabled: !!student,
  })

  if (!student) return null

  const isLoading = analyticsLoading || subjectsLoading || weakAreasLoading

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
              <h1 className="text-2xl font-bold text-gray-900">Progress Dashboard</h1>
              <p className="mt-1 text-sm text-gray-600">
                Track your learning journey and mastery
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Hero Stats Row */}
        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-28 animate-pulse rounded-xl bg-gray-200" />
            ))}
          </div>
        ) : analytics ? (
          <div className="grid gap-6 md:grid-cols-4">
            <StatCard
              icon={<Clock className="h-6 w-6" />}
              title="Total Learning Time"
              value={`${Math.floor(analytics.total_learning_time_minutes / 60)}h ${analytics.total_learning_time_minutes % 60}m`}
              color="blue"
            />
            <StatCard
              icon={<BookOpen className="h-6 w-6" />}
              title="Topics Studied"
              value={analytics.topics_studied.toString()}
              color="purple"
            />
            <StatCard
              icon={<CheckCircle className="h-6 w-6" />}
              title="Topics Completed"
              value={analytics.topics_completed.toString()}
              color="green"
            />
            <StatCard
              icon={<TrendingUp className="h-6 w-6" />}
              title="Overall Progress"
              value={`${Math.round(analytics.overall_progress)}%`}
              color="orange"
            />
          </div>
        ) : (
          <EmptyState message="No analytics data available yet. Start learning to see your progress!" />
        )}

        {/* Weekly Activity + Mastery Overview */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Weekly Activity */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-lg bg-indigo-100 p-2 text-indigo-600">
                <Activity className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Weekly Activity</h2>
            </div>
            {analyticsLoading ? (
              <div className="h-24 animate-pulse rounded-lg bg-gray-100" />
            ) : analytics ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-lg bg-gray-50 p-4">
                  <p className="text-sm text-gray-600">Sessions This Week</p>
                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {analytics.weekly_sessions}
                  </p>
                </div>
                <div className="rounded-lg bg-gray-50 p-4">
                  <p className="text-sm text-gray-600">Time This Week</p>
                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {`${Math.floor(analytics.weekly_time_minutes / 60)}h ${analytics.weekly_time_minutes % 60}m`}
                  </p>
                </div>
                <div className="rounded-lg bg-gray-50 p-4">
                  <p className="text-sm text-gray-600">Avg Quiz Score</p>
                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {Math.round(analytics.average_quiz_score)}%
                  </p>
                </div>
                <div className="rounded-lg bg-gray-50 p-4">
                  <p className="text-sm text-gray-600">Avg Worksheet Score</p>
                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {Math.round(analytics.average_worksheet_score)}%
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No activity data yet.</p>
            )}
          </div>

          {/* Mastery Overview Chart */}
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-lg bg-green-100 p-2 text-green-600">
                <Target className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Mastery Overview</h2>
            </div>
            {analyticsLoading ? (
              <div className="h-48 animate-pulse rounded-lg bg-gray-100" />
            ) : analytics ? (
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Completed', value: analytics.overall_progress },
                        { name: 'Remaining', value: 100 - analytics.overall_progress },
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      startAngle={90}
                      endAngle={-270}
                      dataKey="value"
                    >
                      <Cell fill="#22c55e" />
                      <Cell fill="#e5e7eb" />
                    </Pie>
                    <Tooltip formatter={(value: number) => `${Math.round(value)}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="text-center">
                  <p className="text-3xl font-bold text-gray-900">
                    {Math.round(analytics.overall_progress)}%
                  </p>
                  <p className={cn('text-sm font-medium', getMasteryColor(analytics.overall_progress))}>
                    {getMasteryLabel(analytics.overall_progress)}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No mastery data yet.</p>
            )}
          </div>
        </div>

        {/* Subject Breakdown */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
              <BarChart3 className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Subject Breakdown</h2>
          </div>
          {subjectsLoading ? (
            <div className="h-64 animate-pulse rounded-lg bg-gray-100" />
          ) : subjects && subjects.length > 0 ? (
            <div className="space-y-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={subjects}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="subject" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value: number, name: string) => [
                      `${Math.round(value)}%`,
                      name === 'average_mastery' ? 'Avg Mastery' : 'Progress',
                    ]}
                  />
                  <Bar dataKey="average_mastery" fill="#3b82f6" name="average_mastery" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="progress_percentage" fill="#22c55e" name="progress_percentage" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>

              {/* Progress bars */}
              <div className="space-y-4">
                {subjects.map((subject) => (
                  <div key={subject.subject}>
                    <div className="mb-1 flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">{subject.subject}</span>
                      <span className="text-sm text-gray-500">
                        {subject.topics_mastered}/{subject.topics_studied} mastered
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-200">
                      <div
                        className="h-2 rounded-full bg-blue-500 transition-all"
                        style={{ width: `${Math.min(subject.progress_percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState message="No subject data available yet. Start studying to see your breakdown!" />
          )}
        </div>

        {/* Weak Areas */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-lg bg-red-100 p-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Areas to Improve</h2>
          </div>
          {weakAreasLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 animate-pulse rounded-lg bg-gray-100" />
              ))}
            </div>
          ) : weakAreas && weakAreas.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {weakAreas.map((area) => (
                <div
                  key={area.topic_id}
                  className="rounded-lg border border-gray-200 p-4"
                >
                  <div className="mb-2 flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{area.topic_name}</h3>
                      {area.subject && (
                        <p className="text-xs text-gray-500">{area.subject}</p>
                      )}
                    </div>
                    <span
                      className={cn(
                        'rounded-full px-2 py-0.5 text-xs font-medium',
                        area.priority >= 150
                          ? 'bg-red-100 text-red-700'
                          : area.priority >= 100
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-gray-100 text-gray-700'
                      )}
                    >
                      {area.priority >= 150 ? 'High' : area.priority >= 100 ? 'Medium' : 'Low'}
                    </span>
                  </div>
                  <p className={cn('text-lg font-bold', getMasteryColor(area.mastery_score))}>
                    {Math.round(area.mastery_score)}%
                    <span className="ml-1 text-xs font-normal text-gray-500">mastery</span>
                  </p>
                  {area.reasons.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {area.reasons.map((reason, idx) => (
                        <li key={idx} className="text-xs text-gray-600">
                          • {reason}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="No weak areas identified. Keep up the great work!" />
          )}
        </div>

        {/* Recent Progress Records */}
        <div className="rounded-xl border border-gray-200 bg-white p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
              <BookOpen className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Recent Progress</h2>
          </div>
          {recordsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 animate-pulse rounded-lg bg-gray-100" />
              ))}
            </div>
          ) : records && records.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b text-gray-500">
                    <th className="pb-3 font-medium">Topic</th>
                    <th className="pb-3 font-medium">Mastery</th>
                    <th className="pb-3 font-medium">Quizzes</th>
                    <th className="pb-3 font-medium">Worksheets</th>
                    <th className="pb-3 font-medium">Time Spent</th>
                    <th className="pb-3 font-medium">Last Practiced</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {records.slice(0, 10).map((record) => (
                    <tr key={record.id} className="text-gray-700">
                      <td className="py-3 font-medium">{record.topic_id}</td>
                      <td className="py-3">
                        <span className={cn('font-semibold', getMasteryColor(record.mastery_level))}>
                          {Math.round(record.mastery_level)}%
                        </span>
                      </td>
                      <td className="py-3">{record.quiz_count}</td>
                      <td className="py-3">{record.worksheet_count}</td>
                      <td className="py-3">{formatTime(record.total_time_spent_seconds)}</td>
                      <td className="py-3 text-gray-500">
                        {record.last_practiced_at ? formatDate(record.last_practiced_at) : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No progress records yet. Complete quizzes and worksheets to track your progress!" />
          )}
        </div>
      </main>
    </div>
  )
}

function StatCard({
  icon,
  title,
  value,
  color,
}: {
  icon: React.ReactNode
  title: string
  value: string
  color: 'blue' | 'green' | 'purple' | 'orange'
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">
      <div className="flex items-center gap-4">
        <div className={`rounded-lg p-3 ${colorClasses[color]}`}>{icon}</div>
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
      <BookOpen className="mx-auto h-10 w-10 text-gray-400" />
      <p className="mt-3 text-sm text-gray-500">{message}</p>
    </div>
  )
}
