'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation } from '@tanstack/react-query'
import { quizzesApi, Quiz, QuizQuestion, QuizAttempt } from '@/lib/api/quizzes'
import { ArrowLeft, CheckCircle, Loader2, Timer, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'

export default function QuizPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const quizId = params.id as string

  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [currentAttempt, setCurrentAttempt] = useState<QuizAttempt | null>(null)
  const [timeRemaining, setTimeRemaining] = useState<number>(0)
  const [hasStarted, setHasStarted] = useState(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const autoSubmitRef = useRef<boolean>(false)

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch quiz
  const { data: quiz, isLoading } = useQuery<Quiz>({
    queryKey: ['quiz', quizId],
    queryFn: () => quizzesApi.get(quizId),
    enabled: !!quizId,
  })

  // Start attempt mutation
  const startMutation = useMutation({
    mutationFn: async () => {
      return quizzesApi.startAttempt(quizId)
    },
    onSuccess: (attempt) => {
      setCurrentAttempt(attempt)
      setHasStarted(true)
      // Set initial time remaining
      if (quiz) {
        setTimeRemaining(quiz.duration_minutes * 60)
      }
      toast.success('Quiz started! Good luck!')
    },
    onError: () => {
      toast.error('Failed to start quiz')
    },
  })

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!currentAttempt) throw new Error('No active attempt')
      return quizzesApi.submit(quizId, currentAttempt.id, answers)
    },
    onSuccess: (submission) => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      const message = autoSubmitRef.current
        ? 'Time\'s up! Quiz auto-submitted.'
        : 'Quiz submitted successfully!'
      toast.success(message)
      router.push(`/quizzes/${quizId}/result`)
    },
    onError: () => {
      toast.error('Failed to submit quiz')
    },
  })

  // Countdown timer
  useEffect(() => {
    if (!hasStarted || !quiz) return

    timerRef.current = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          // Time's up! Auto-submit
          if (timerRef.current) {
            clearInterval(timerRef.current)
          }
          autoSubmitRef.current = true
          submitMutation.mutate()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [hasStarted, quiz])

  const handleAnswerChange = (questionNumber: number, answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionNumber]: answer,
    }))
  }

  const handleSubmit = () => {
    // Check if all questions are answered
    const unanswered = quiz?.questions.filter(
      (q) => !answers[q.question_number]
    )

    if (unanswered && unanswered.length > 0) {
      const confirm = window.confirm(
        `You have ${unanswered.length} unanswered question(s). Submit anyway?`
      )
      if (!confirm) return
    }

    autoSubmitRef.current = false
    submitMutation.mutate()
  }

  const handleStart = () => {
    startMutation.mutate()
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getTimerColor = () => {
    if (!quiz) return 'text-gray-900'
    const percentage = (timeRemaining / (quiz.duration_minutes * 60)) * 100
    if (percentage <= 10) return 'text-red-600'
    if (percentage <= 30) return 'text-orange-600'
    return 'text-blue-600'
  }

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

  if (!quiz) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Quiz not found</h2>
          <Link
            href="/quizzes"
            className="mt-4 inline-block text-blue-600 hover:text-blue-700"
          >
            Back to Quizzes
          </Link>
        </div>
      </div>
    )
  }

  // Start screen
  if (!hasStarted) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="border-b bg-white">
          <div className="container mx-auto px-4 py-6">
            <Link
              href="/quizzes"
              className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Quizzes
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">{quiz.title}</h1>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="mx-auto max-w-2xl">
            <div className="rounded-xl border border-gray-200 bg-white p-8">
              <div className="text-center">
                <Timer className="mx-auto h-16 w-16 text-blue-600" />
                <h2 className="mt-4 text-2xl font-bold text-gray-900">
                  Ready to start?
                </h2>
                <p className="mt-2 text-gray-600">
                  You have {quiz.duration_minutes} minutes to complete this quiz
                </p>
              </div>

              <div className="mt-8 space-y-4">
                <div className="flex items-center justify-between rounded-lg bg-gray-50 p-4">
                  <span className="text-sm font-medium text-gray-700">Questions:</span>
                  <span className="text-sm text-gray-900">{quiz.total_questions}</span>
                </div>
                <div className="flex items-center justify-between rounded-lg bg-gray-50 p-4">
                  <span className="text-sm font-medium text-gray-700">Duration:</span>
                  <span className="text-sm text-gray-900">{quiz.duration_minutes} minutes</span>
                </div>
                <div className="flex items-center justify-between rounded-lg bg-gray-50 p-4">
                  <span className="text-sm font-medium text-gray-700">Difficulty:</span>
                  <span className="text-sm capitalize text-gray-900">{quiz.difficulty}</span>
                </div>
              </div>

              <div className="mt-6 rounded-lg bg-amber-50 p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-600" />
                  <div className="text-sm text-amber-900">
                    <p className="font-medium">Important:</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-800">
                      <li>The timer will start as soon as you begin</li>
                      <li>The quiz will auto-submit when time runs out</li>
                      <li>You can submit early if you finish before time</li>
                    </ul>
                  </div>
                </div>
              </div>

              <button
                onClick={handleStart}
                disabled={startMutation.isPending}
                className="mt-8 w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              >
                {startMutation.isPending ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Starting...
                  </span>
                ) : (
                  'Start Quiz'
                )}
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  // Quiz in progress
  const answeredCount = Object.keys(answers).length
  const progress = (answeredCount / quiz.total_questions) * 100

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Timer */}
      <header className="sticky top-0 z-10 border-b bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <h1 className="text-lg font-semibold text-gray-900">{quiz.title}</h1>
              <p className="text-sm text-gray-600">
                {answeredCount}/{quiz.total_questions} answered
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Countdown Timer */}
              <div className={`flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 ${getTimerColor()}`}>
                <Timer className="h-5 w-5" />
                <span className="text-lg font-bold">
                  {formatTime(timeRemaining)}
                </span>
              </div>

              <button
                onClick={handleSubmit}
                disabled={submitMutation.isPending}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              >
                {submitMutation.isPending ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Submitting...
                  </span>
                ) : (
                  'Submit Quiz'
                )}
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {quiz.questions.map((question) => (
            <QuestionCard
              key={question.question_number}
              question={question}
              answer={answers[question.question_number] || ''}
              onAnswerChange={(answer) =>
                handleAnswerChange(question.question_number, answer)
              }
            />
          ))}
        </div>
      </main>
    </div>
  )
}

function QuestionCard({
  question,
  answer,
  onAnswerChange,
}: {
  question: QuizQuestion
  answer: string
  onAnswerChange: (answer: string) => void
}) {
  const isAnswered = answer.trim() !== ''

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">
      <div className="flex items-start gap-4">
        <div
          className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold ${
            isAnswered
              ? 'bg-blue-100 text-blue-600'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          {question.question_number}
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between">
            <p className="text-base font-medium text-gray-900">{question.question}</p>
            {isAnswered && (
              <CheckCircle className="ml-2 h-5 w-5 flex-shrink-0 text-green-600" />
            )}
          </div>

          <div className="mt-1 text-xs text-gray-500">{question.type}</div>

          {/* Answer Input */}
          <div className="mt-4">
            {question.type === 'MCQ' && question.options ? (
              <div className="space-y-2">
                {question.options.map((option, index) => (
                  <label
                    key={index}
                    className={`flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition ${
                      answer === option
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${question.question_number}`}
                      value={option}
                      checked={answer === option}
                      onChange={(e) => onAnswerChange(e.target.value)}
                      className="h-4 w-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-900">{option}</span>
                  </label>
                ))}
              </div>
            ) : question.type === 'True/False' ? (
              <div className="flex gap-4">
                <label
                  className={`flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-lg border p-4 transition ${
                    answer === 'True'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.question_number}`}
                    value="True"
                    checked={answer === 'True'}
                    onChange={(e) => onAnswerChange(e.target.value)}
                    className="h-4 w-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-900">True</span>
                </label>
                <label
                  className={`flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-lg border p-4 transition ${
                    answer === 'False'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.question_number}`}
                    value="False"
                    checked={answer === 'False'}
                    onChange={(e) => onAnswerChange(e.target.value)}
                    className="h-4 w-4 text-blue-600 focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-900">False</span>
                </label>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
