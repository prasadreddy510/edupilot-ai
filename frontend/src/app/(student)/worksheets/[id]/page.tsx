'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation } from '@tanstack/react-query'
import { worksheetsApi, Worksheet, Question } from '@/lib/api/worksheets'
import { ArrowLeft, CheckCircle, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

export default function WorksheetPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const worksheetId = params.id as string

  const [answers, setAnswers] = useState<Record<string, string>>({})

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch worksheet
  const { data: worksheet, isLoading } = useQuery<Worksheet>({
    queryKey: ['worksheet', worksheetId],
    queryFn: () => worksheetsApi.get(worksheetId),
    enabled: !!worksheetId,
  })

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      return worksheetsApi.submit(worksheetId, answers)
    },
    onSuccess: (submission) => {
      toast.success('Worksheet submitted successfully!')
      router.push(`/student/worksheets/${worksheetId}/result`)
    },
    onError: () => {
      toast.error('Failed to submit worksheet')
    },
  })

  const handleAnswerChange = (questionNumber: number, answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionNumber]: answer,
    }))
  }

  const handleSubmit = () => {
    // Check if all questions are answered
    const unanswered = worksheet?.questions.filter(
      (q) => !answers[q.question_number]
    )

    if (unanswered && unanswered.length > 0) {
      const confirm = window.confirm(
        `You have ${unanswered.length} unanswered question(s). Submit anyway?`
      )
      if (!confirm) return
    }

    submitMutation.mutate()
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

  if (!worksheet) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Worksheet not found</h2>
          <Link
            href="/student/worksheets"
            className="mt-4 inline-block text-blue-600 hover:text-blue-700"
          >
            Back to Worksheets
          </Link>
        </div>
      </div>
    )
  }

  const answeredCount = Object.keys(answers).length
  const progress = (answeredCount / worksheet.total_questions) * 100

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link
              href="/student/worksheets"
              className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>

            <div className="text-center">
              <h1 className="text-lg font-semibold text-gray-900">{worksheet.title}</h1>
              <p className="text-sm text-gray-600">
                {answeredCount}/{worksheet.total_questions} answered
              </p>
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
                'Submit Worksheet'
              )}
            </button>
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
          {worksheet.questions.map((question) => (
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
  question: Question
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

          <div className="mt-1 text-xs text-gray-500">
            {question.type} • {question.points} {question.points === 1 ? 'point' : 'points'}
          </div>

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
            ) : (
              <textarea
                value={answer}
                onChange={(e) => onAnswerChange(e.target.value)}
                placeholder="Type your answer here..."
                rows={question.type === 'Short Answer' ? 3 : 1}
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
