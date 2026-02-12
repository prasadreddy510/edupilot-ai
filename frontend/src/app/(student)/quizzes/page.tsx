'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import { quizzesApi, QuizListItem } from '@/lib/api/quizzes'
import {
  ArrowLeft,
  Clock,
  Trophy,
  TrendingUp,
  Plus,
  Timer,
} from 'lucide-react'

export default function QuizzesPage() {
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch quizzes
  const { data: quizzes, isLoading } = useQuery<QuizListItem[]>({
    queryKey: ['quizzes'],
    queryFn: () => quizzesApi.list(undefined, 50),
    enabled: !!student,
  })

  if (!student) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-6">
          <Link
            href="/dashboard"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Timed Quizzes</h1>
              <p className="mt-2 text-sm text-gray-600">
                Test your knowledge with time-limited quizzes
              </p>
            </div>

            <Link
              href="/quizzes/generate"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Start New Quiz
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 animate-pulse rounded-xl bg-gray-200" />
            ))}
          </div>
        ) : quizzes && quizzes.length > 0 ? (
          <div className="space-y-4">
            {quizzes.map((quiz) => (
              <QuizCard key={quiz.id} quiz={quiz} />
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
            <Timer className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              No quizzes yet
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Start your first quiz to test your knowledge
            </p>
            <Link
              href="/quizzes/generate"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Start New Quiz
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}

function QuizCard({ quiz }: { quiz: QuizListItem }) {
  const router = useRouter()

  const difficultyColors = {
    easy: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-700',
    hard: 'bg-red-100 text-red-700',
  }

  const handleClick = () => {
    if (quiz.total_attempts > 0) {
      // View stats/attempts
      router.push(`/quizzes/${quiz.id}/attempts`)
    } else {
      // Start first attempt
      router.push(`/quizzes/${quiz.id}`)
    }
  }

  return (
    <div
      onClick={handleClick}
      className="group cursor-pointer rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600">
              {quiz.title}
            </h3>
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                difficultyColors[quiz.difficulty as keyof typeof difficultyColors] ||
                'bg-gray-100 text-gray-700'
              }`}
            >
              {quiz.difficulty}
            </span>
          </div>

          <p className="mt-1 text-sm text-gray-600">{quiz.topic_name}</p>

          <div className="mt-4 flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Timer className="h-4 w-4" />
              <span>{quiz.total_questions} questions</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>{quiz.duration_minutes} minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              <span>{quiz.total_attempts} {quiz.total_attempts === 1 ? 'attempt' : 'attempts'}</span>
            </div>
          </div>
        </div>

        <div className="ml-4 text-right">
          {quiz.best_score !== null && quiz.best_score !== undefined ? (
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-amber-100 px-4 py-2 text-sm font-medium text-amber-700">
                <Trophy className="h-4 w-4" />
                {quiz.best_score.toFixed(0)}%
              </div>
              <p className="text-xs text-gray-500">Best Score</p>
              {quiz.latest_score !== null && quiz.latest_score !== undefined && (
                <p className="text-xs text-gray-600">
                  Latest: {quiz.latest_score.toFixed(0)}%
                </p>
              )}
            </div>
          ) : (
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700">
              <Timer className="h-4 w-4" />
              Not attempted
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
