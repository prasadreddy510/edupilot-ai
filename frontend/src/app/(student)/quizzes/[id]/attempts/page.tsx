'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import { quizzesApi, QuizAttempt, Quiz } from '@/lib/api/quizzes'
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Timer,
  Loader2,
} from 'lucide-react'

export default function QuizAttemptsPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const quizId = params.id as string

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch quiz
  const { data: quiz } = useQuery<Quiz>({
    queryKey: ['quiz', quizId],
    queryFn: () => quizzesApi.get(quizId),
    enabled: !!quizId,
  })

  // Fetch attempts
  const { data: attempts, isLoading } = useQuery<QuizAttempt[]>({
    queryKey: ['quiz-attempts', quizId],
    queryFn: () => quizzesApi.getAttempts(quizId),
    enabled: !!quizId,
  })

  if (!student) {
    return null
  }

  const bestScore = attempts && attempts.length > 0
    ? Math.max(...attempts.map((a) => a.percentage || 0))
    : 0

  const averageScore = attempts && attempts.length > 0
    ? attempts.reduce((sum, a) => sum + (a.percentage || 0), 0) / attempts.length
    : 0

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-6">
          <Link
            href="/student/quizzes"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Quizzes
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {quiz?.title || 'Quiz'} - All Attempts
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                View all your attempts and track your improvement
              </p>
            </div>

            <Link
              href={`/student/quizzes/${quizId}`}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              Take Quiz Again
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Stats Summary */}
          {attempts && attempts.length > 0 && (
            <div className="grid gap-6 md:grid-cols-3">
              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-amber-100 p-3">
                    <TrendingUp className="h-6 w-6 text-amber-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Best Score</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {bestScore.toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-100 p-3">
                    <Timer className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Average Score</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {averageScore.toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-gray-200 bg-white p-6">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-green-100 p-3">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Attempts</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {attempts.length}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Attempts List */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Attempt History</h3>

            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              </div>
            ) : attempts && attempts.length > 0 ? (
              <div className="space-y-4">
                {attempts.map((attempt, index) => (
                  <AttemptCard
                    key={attempt.id}
                    attempt={attempt}
                    attemptNumber={attempts.length - index}
                    isBest={attempt.percentage === bestScore}
                  />
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
                <Timer className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  No attempts yet
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  Start your first quiz attempt
                </p>
                <Link
                  href={`/student/quizzes/${quizId}`}
                  className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
                >
                  Start Quiz
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

function AttemptCard({
  attempt,
  attemptNumber,
  isBest,
}: {
  attempt: QuizAttempt
  attemptNumber: number
  isBest: boolean
}) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div
      className={`rounded-xl border-2 bg-white p-6 ${
        isBest ? 'border-amber-300 bg-amber-50/30' : 'border-gray-200'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h4 className="text-lg font-semibold text-gray-900">
              Attempt #{attemptNumber}
            </h4>
            {isBest && (
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
                🏆 Best Score
              </span>
            )}
            {attempt.passed ? (
              <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                <CheckCircle className="inline h-3 w-3 mr-1" />
                Passed
              </span>
            ) : (
              <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-700">
                <XCircle className="inline h-3 w-3 mr-1" />
                Failed
              </span>
            )}
          </div>

          <p className="mt-1 text-sm text-gray-600">
            {attempt.submitted_at && formatDate(attempt.submitted_at)}
          </p>

          <div className="mt-4 flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-700">Score:</span>
              <span className="font-bold text-gray-900">
                {attempt.score}/{attempt.max_score} ({attempt.percentage?.toFixed(0)}%)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>
                {attempt.time_taken_seconds
                  ? formatTime(attempt.time_taken_seconds)
                  : 'N/A'}
              </span>
            </div>
            {attempt.time_exceeded && (
              <span className="rounded-full bg-orange-100 px-2 py-1 text-xs font-medium text-orange-700">
                Time Exceeded
              </span>
            )}
          </div>

          {/* Improvement indicator */}
          {attempt.improvement_data && !attempt.improvement_data.is_first_attempt && (
            <div className="mt-3 flex items-center gap-2 text-sm">
              {attempt.improvement_data.improvement > 0 ? (
                <>
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-green-700">
                    +{attempt.improvement_data.improvement.toFixed(1)}% from previous
                  </span>
                </>
              ) : attempt.improvement_data.improvement < 0 ? (
                <>
                  <TrendingUp className="h-4 w-4 rotate-180 text-red-600" />
                  <span className="text-red-700">
                    {attempt.improvement_data.improvement.toFixed(1)}% from previous
                  </span>
                </>
              ) : (
                <span className="text-gray-600">Same as previous attempt</span>
              )}
            </div>
          )}
        </div>

        <div className="ml-4">
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-900">
              {attempt.percentage?.toFixed(0)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
