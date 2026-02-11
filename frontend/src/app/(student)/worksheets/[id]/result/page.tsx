'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import { worksheetsApi, WorksheetSubmission, GradedAnswer } from '@/lib/api/worksheets'
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  TrendingUp,
  RotateCcw,
  Loader2,
  Award,
} from 'lucide-react'

export default function WorksheetResultPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const worksheetId = params.id as string

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch latest submission
  const { data: submissions, isLoading } = useQuery<WorksheetSubmission[]>({
    queryKey: ['worksheet-submissions', worksheetId],
    queryFn: () => worksheetsApi.getSubmissions(worksheetId),
    enabled: !!worksheetId,
  })

  const latestSubmission = submissions?.[0]

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

  if (!latestSubmission) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">No submission found</h2>
          <Link
            href={`/student/worksheets/${worksheetId}`}
            className="mt-4 inline-block text-blue-600 hover:text-blue-700"
          >
            Start Worksheet
          </Link>
        </div>
      </div>
    )
  }

  const correctCount = latestSubmission.graded_answers.filter((a) => a.is_correct).length

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-6">
          <Link
            href="/student/worksheets"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Worksheets
          </Link>

          <h1 className="text-3xl font-bold text-gray-900">Worksheet Results</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Score Card */}
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
            <div
              className={`px-8 py-6 ${
                latestSubmission.passed
                  ? 'bg-gradient-to-r from-green-50 to-emerald-50'
                  : 'bg-gradient-to-r from-red-50 to-orange-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    {latestSubmission.passed ? (
                      <Award className="h-8 w-8 text-green-600" />
                    ) : (
                      <TrendingUp className="h-8 w-8 text-orange-600" />
                    )}
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {latestSubmission.passed ? 'Great Job!' : 'Keep Practicing!'}
                      </h2>
                      <p className="text-sm text-gray-600">
                        {latestSubmission.passed
                          ? 'You passed this worksheet'
                          : 'Try again to improve your score'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-4xl font-bold text-gray-900">
                    {latestSubmission.percentage.toFixed(0)}%
                  </div>
                  <p className="text-sm text-gray-600">
                    {latestSubmission.score}/{latestSubmission.max_score} points
                  </p>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-4">
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Correct</p>
                  <p className="mt-1 text-2xl font-bold text-green-600">
                    {correctCount}
                  </p>
                </div>
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Incorrect</p>
                  <p className="mt-1 text-2xl font-bold text-red-600">
                    {latestSubmission.graded_answers.length - correctCount}
                  </p>
                </div>
                <div className="rounded-lg bg-white p-4">
                  <p className="text-sm font-medium text-gray-600">Total</p>
                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {latestSubmission.graded_answers.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4 p-6">
              <Link
                href={`/student/worksheets/${worksheetId}`}
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 transition hover:bg-gray-50"
              >
                <RotateCcw className="h-4 w-4" />
                Try Again
              </Link>
              <Link
                href="/student/worksheets/generate"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700"
              >
                Generate New Worksheet
              </Link>
            </div>
          </div>

          {/* Detailed Results */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Detailed Results</h3>
            {latestSubmission.graded_answers.map((answer) => (
              <AnswerCard key={answer.question_number} answer={answer} />
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

function AnswerCard({ answer }: { answer: GradedAnswer }) {
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
              <span className="text-sm font-medium text-gray-600">
                {answer.score}/{answer.max_score}
              </span>
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

            {/* Feedback */}
            {answer.feedback && (
              <div>
                <p className="text-xs font-medium text-gray-500">Feedback:</p>
                <p className="mt-1 rounded-lg bg-blue-50 p-3 text-sm text-blue-900">
                  {answer.feedback}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
