'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '@/lib/api/client'
import { ArrowLeft, BookOpen, Loader2, RefreshCw, Bookmark, BookmarkCheck, Clock } from 'lucide-react'
import { Topic } from '@/types'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { toast } from 'sonner'
import { learningApi, LearningSession } from '@/lib/api/learning'

interface ExplanationResponse {
  topic_id: string
  topic_name: string
  subject: string
  grade: number
  explanation: string
  difficulty: string
}

const DIFFICULTY_LEVELS = [
  { value: 'easy', label: 'Easy', color: 'bg-green-100 text-green-700' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'hard', label: 'Hard', color: 'bg-red-100 text-red-700' },
]

export default function LearnTopicPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const topicId = params.topicId as string

  const [difficulty, setDifficulty] = useState<string>('medium')
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [currentSession, setCurrentSession] = useState<LearningSession | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Start learning session when page loads
  useEffect(() => {
    if (!topicId || !isAuthenticated) return

    const startSession = async () => {
      try {
        const session = await learningApi.startSession(topicId)
        setCurrentSession(session)

        // Start the timer
        timerRef.current = setInterval(() => {
          setElapsedTime((prev) => prev + 1)
        }, 1000)
      } catch (error) {
        console.error('Failed to start learning session:', error)
      }
    }

    startSession()

    // Cleanup: end session when component unmounts
    return () => {
      if (currentSession) {
        learningApi.endSession(currentSession.id, false).catch(console.error)
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [topicId, isAuthenticated])

  // Fetch topic details
  const { data: topic } = useQuery<Topic>({
    queryKey: ['topic', topicId],
    queryFn: async () => {
      return apiClient.get(`/api/v1/topics/${topicId}`)
    },
    enabled: !!topicId,
  })

  // Fetch explanation
  const {
    data: explanation,
    isLoading,
    refetch,
  } = useQuery<ExplanationResponse>({
    queryKey: ['explanation', topicId, difficulty],
    queryFn: async () => {
      return apiClient.post(`/api/v1/topics/${topicId}/explain`, {
        difficulty,
      })
    },
    enabled: !!topicId,
    retry: 1,
  })

  // Mutation for regenerating explanation
  const regenerateMutation = useMutation({
    mutationFn: async () => {
      return apiClient.post(`/api/v1/topics/${topicId}/explain`, {
        difficulty,
      })
    },
    onSuccess: () => {
      refetch()
      toast.success('Explanation regenerated!')
    },
    onError: () => {
      toast.error('Failed to regenerate explanation')
    },
  })

  const handleDifficultyChange = (newDifficulty: string) => {
    setDifficulty(newDifficulty)
  }

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked)
    toast.success(isBookmarked ? 'Bookmark removed' : 'Bookmark added')
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Mutation for marking topic as complete
  const completeMutation = useMutation({
    mutationFn: async () => {
      if (!currentSession) throw new Error('No active session')
      return learningApi.endSession(currentSession.id, true)
    },
    onSuccess: () => {
      toast.success('Topic marked as complete! Great job! 🎉')
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      router.push('/student/dashboard')
    },
    onError: () => {
      toast.error('Failed to mark topic as complete')
    },
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
            href="/student/dashboard"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {topic?.name || 'Loading...'}
              </h1>
              {explanation && (
                <p className="mt-2 text-sm text-gray-600">
                  {explanation.subject} • Grade {explanation.grade}
                </p>
              )}
              {currentSession && (
                <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700">
                  <Clock className="h-4 w-4" />
                  <span>Learning time: {formatTime(elapsedTime)}</span>
                </div>
              )}
            </div>

            <button
              onClick={handleBookmark}
              className="rounded-lg p-2 transition hover:bg-gray-100"
              title={isBookmarked ? 'Remove bookmark' : 'Bookmark topic'}
            >
              {isBookmarked ? (
                <BookmarkCheck className="h-5 w-5 text-blue-600" />
              ) : (
                <Bookmark className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl">
          {/* Controls */}
          <div className="mb-6 flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700">Difficulty:</span>
              <div className="flex gap-2">
                {DIFFICULTY_LEVELS.map((level) => (
                  <button
                    key={level.value}
                    onClick={() => handleDifficultyChange(level.value)}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                      difficulty === level.value
                        ? level.color
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {level.label}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => regenerateMutation.mutate()}
              disabled={regenerateMutation.isPending}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
            >
              {regenerateMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Regenerating...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Regenerate
                </>
              )}
            </button>
          </div>

          {/* Explanation Content */}
          <div className="rounded-xl border border-gray-200 bg-white p-8">
            {isLoading ? (
              <div className="space-y-4">
                <div className="h-6 w-3/4 animate-pulse rounded bg-gray-200" />
                <div className="h-4 w-full animate-pulse rounded bg-gray-200" />
                <div className="h-4 w-5/6 animate-pulse rounded bg-gray-200" />
                <div className="h-4 w-full animate-pulse rounded bg-gray-200" />
                <div className="h-4 w-4/6 animate-pulse rounded bg-gray-200" />
              </div>
            ) : explanation ? (
              <div className="prose prose-blue max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    h1: ({ children }) => (
                      <h1 className="text-3xl font-bold text-gray-900">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="mt-8 text-2xl font-bold text-gray-900">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="mt-6 text-xl font-semibold text-gray-900">{children}</h3>
                    ),
                    p: ({ children }) => (
                      <p className="my-4 leading-relaxed text-gray-700">{children}</p>
                    ),
                    ul: ({ children }) => (
                      <ul className="my-4 ml-6 list-disc space-y-2 text-gray-700">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="my-4 ml-6 list-decimal space-y-2 text-gray-700">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                    code: ({ inline, children, ...props }: any) =>
                      inline ? (
                        <code
                          className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-mono text-gray-800"
                          {...props}
                        >
                          {children}
                        </code>
                      ) : (
                        <code
                          className="block rounded-lg bg-gray-900 p-4 text-sm text-gray-100"
                          {...props}
                        >
                          {children}
                        </code>
                      ),
                    blockquote: ({ children }) => (
                      <blockquote className="my-4 border-l-4 border-blue-500 bg-blue-50 p-4 italic text-gray-700">
                        {children}
                      </blockquote>
                    ),
                  }}
                >
                  {explanation.explanation}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="py-12 text-center">
                <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  Failed to load explanation
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  Please try refreshing the page or selecting a different difficulty.
                </p>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <Link
              href={`/student/worksheets/generate?topic=${topicId}`}
              className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
            >
              <div>
                <h3 className="font-semibold text-gray-900">Practice Worksheet</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Generate practice questions
                </p>
              </div>
              <span className="text-2xl">📝</span>
            </Link>

            <Link
              href={`/student/quizzes?topic=${topicId}`}
              className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
            >
              <div>
                <h3 className="font-semibold text-gray-900">Take Quiz</h3>
                <p className="mt-1 text-sm text-gray-600">Test your understanding</p>
              </div>
              <span className="text-2xl">🎯</span>
            </Link>

            <button
              onClick={() => completeMutation.mutate()}
              disabled={completeMutation.isPending || !currentSession}
              className="flex items-center justify-between rounded-xl border border-green-200 bg-green-50 p-6 transition hover:bg-green-100 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-50"
            >
              <div>
                <h3 className="font-semibold text-green-900">Mark as Complete</h3>
                <p className="mt-1 text-sm text-green-700">Finished learning this topic</p>
              </div>
              <span className="text-2xl">✅</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
