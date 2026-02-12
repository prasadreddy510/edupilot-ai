'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@antml:invoke name="@tanstack/react-query'
import { quizzesApi, QuizAttempt, GradedQuizAnswer } from '@/lib/api/quizzes'
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  RotateCcw,
  Loader2,
  Trophy,
  Clock,
  AlertTriangle,
} from 'lucide-react'

export default function QuizResultPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const quizId = params.id as string

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch latest attempt
  const { data: attempts, isLoading } = useQuery<QuizAttempt[]>({
    queryKey: ['quiz-attempts', quizId],
    queryFn: () => quizzesApi.getAttempts(quizId),
    enabled: !!quizId,
  })

  const latestAttempt = attempts?.[0]

  if (!student) {
    return null
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (!latestAttempt || !latestAttempt.submitted_at) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">No submission found</h2>
          <Link
            href={`/quizzes/${quizId}`}
            className="mt-4 inline-block text-blue-600 hover:text-blue-700"
          >
            Start Quiz
          </Link>
        </div>
      </div>
    )
  }

  const correctCount = latestAttempt.graded_answers?.filter((a) => a.is_correct).length || 0
  const improvementData = latestAttempt.improvement_data

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
            href="/quizzes"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Quizzes
          </Link>

          <h1 className="text-3xl font-bold text-gray-900">Quiz Results</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Score Card */}
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <div
              className={`px-8 py-6 ${
                latestAttempt.passed
                  ? 'bg-gradient-to-r from-green-50 to-emerald-50'
                  : 'bg-gradient-to-r from-red-50 to-orange-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    {latestAttempt.passed ? (
                      <Trophy className="h-8 w-8 text-green-600" />
                    ) : (
                      <TrendingUp className="h-8 w-8 text-orange-600" />
                    )}
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {latestAttempt.passed ? 'Great Job!' : 'Keep Practicing!'}
                      </h2>
                      <p className="text-sm text-gray-600">
                        {latestAttempt.passed
                          ? 'You passed this quiz'
                          : 'Try again to improve your score'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-4xl font-bold text-gray-900">
                    {latestAttempt.percentage?.toFixed(0)}%
                  </div>
                  <p className="text-sm text-gray-600">
                    {latestAttempt.score}/{latestAttempt.max_score} correct
                  </p>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-4 gap-4">
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Correct</p>
                  <p className="mt-1 text-2xl font-bold text-green-600">
                    {correctCount}
                  </p>
                </div>
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Incorrect</p>
                  <p className="mt-1 text-2xl font-bold text-red-600">
                    {(latestAttempt.graded_answers?.length || 0) - correctCount}
                  </p>
                </div>
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Time Taken</p>
                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {latestAttempt.time_taken_seconds
                      ? formatTime(latestAttempt.time_taken_seconds)
                      : 'N/A'}
                  </p>
                </div>
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Status</p>
                  <p className="mt-1 flex items-center gap-1 text-sm font-bold">
                    {latestAttempt.time_exceeded ? (
                      <>
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                        <span className="text-orange-600">Time Exceeded</span>
                      </>
                    ) : (
                      <>
                        <Clock className="h-4 w-4 text-green-600" />
                        <span className="text-green-600">On Time</span>
                      </>
                    )}
                  </p>
                </div>
              </div>
            </div>

            {/* Improvement Section */}
            {improvementData && !improvementData.is_first_attempt && (
              <div className="border-t bg-blue-50 px-8 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {improvementData.improvement >= 0 ? (
                      <TrendingUp className="h-5 w-5 text-green-600" />
                    ) : (
                      <TrendingDown className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {improvementData.improvement >= 0
                          ? `Improved by ${improvementData.improvement.toFixed(1)}%`
                          : `Decreased by ${Math.abs(improvementData.improvement).toFixed(1)}%`}
                      </p>
                      <p className="text-xs text-gray-600">
                        Attempt {improvementData.total_attempts} •
                        Best: {improvementData.best_score.toFixed(0)}% •
                        Avg: {improvementData.average_score.toFixed(0)}%
                      </p>
                    </div>
                  </div>

                  {improvementData.is_best_score && (
                    <div className="rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-700">
                      🏆 New Best Score!
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="flex items-center justify-center gap-4 p-6">
              <Link
                href={`/quizzes/${quizId}`}
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 transition hover:bg-gray-50"
              >
                <RotateCcw className="h-4 w-4" />
                Try Again
              </Link>
              <Link
                href={`/quizzes/${quizId}/attempts`}
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 transition hover:bg-gray-50"
              >
                View All Attempts
              </Link>
              <Link
                href="/quizzes/generate"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700"
              >
                Start New Quiz
              </Link>
            </div>
          </div>

          {/* Detailed Results */}
          {latestAttempt.graded_answers && latestAttempt.graded_answers.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Detailed Results</h3>
              {latestAttempt.graded_answers.map((answer) => (
                <AnswerCard key={answer.question_number} answer={answer} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function AnswerCard({ answer }: { answer: GradedQuizAnswer }) {
  return (
    <div
      className={`rounded-xl border-2 bg-white p-6 ${
        answer.is_correct
          ? 'border-green-200 bg-green-50/30'
          : 'border-red-200 bg-red-50/30'
      }`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold ${
            answer.is_correct
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {answer.question_number}
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between">
            <p className="text-base font-medium text-gray-900">{answer.question}</p>
            <div className="ml-4 flex items-center gap-2">
              {answer.is_correct ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
            </div>
          </div>

          <div className="mt-4 space-y-3">
            {/* Student Answer */}
            <div>
              <p className="text-xs font-medium text-gray-500">Your Answer:</p>
              <p
                className={`mt-1 rounded-lg p-3 text-sm ${
                  answer.is_correct
                    ? 'bg-green-100 text-green-900'
                    : 'bg-red-100 text-red-900'
                }`}
              >
                {answer.student_answer || '(No answer provided)'}
              </p>
            </div>

            {/* Correct Answer */}
            {!answer.is_correct && answer.correct_answer && (
              <div>
                <p className="text-xs font-medium text-gray-500">Correct Answer:</p>
                <p className="mt-1 rounded-lg bg-emerald-100 p-3 text-sm text-emerald-900">
                  {answer.correct_answer}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
