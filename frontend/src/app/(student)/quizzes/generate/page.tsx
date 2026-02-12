'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '@/lib/api/client'
import { quizzesApi } from '@/lib/api/quizzes'
import { Subject, Topic } from '@/types'
import { ArrowLeft, Loader2, Timer } from 'lucide-react'
import { toast } from 'sonner'

const DIFFICULTY_LEVELS = [
  { value: 'easy', label: 'Easy', color: 'bg-green-100 text-green-700 hover:bg-green-200' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' },
  { value: 'hard', label: 'Hard', color: 'bg-red-100 text-red-700 hover:bg-red-200' },
]

const QUIZ_OPTIONS = [
  { questions: 5, duration: 10 },
  { questions: 10, duration: 20 },
  { questions: 15, duration: 30 },
  { questions: 20, duration: 40 },
]

export default function GenerateQuizPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isAuthenticated, student } = useAuthStore()

  const topicParam = searchParams.get('topic')

  const [selectedSubject, setSelectedSubject] = useState<string>('')
  const [selectedTopic, setSelectedTopic] = useState<string>(topicParam || '')
  const [difficulty, setDifficulty] = useState<string>('medium')
  const [numQuestions, setNumQuestions] = useState<number>(10)

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch subjects
  const { data: subjects } = useQuery<Subject[]>({
    queryKey: ['subjects', student?.grade],
    queryFn: async () => {
      return apiClient.get(`/api/v1/subjects?grade=${student?.grade}`)
    },
    enabled: !!student?.grade,
  })

  // Fetch topics for selected subject
  const { data: topics } = useQuery<Topic[]>({
    queryKey: ['topics', selectedSubject],
    queryFn: async () => {
      return apiClient.get(`/api/v1/topics?subject_id=${selectedSubject}`)
    },
    enabled: !!selectedSubject,
  })

  // Generate quiz mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      if (!selectedTopic) {
        throw new Error('Please select a topic')
      }

      return quizzesApi.generate({
        topic_id: selectedTopic,
        num_questions: numQuestions,
        difficulty: difficulty as 'easy' | 'medium' | 'hard',
      })
    },
    onSuccess: (quiz) => {
      toast.success('Quiz generated successfully!')
      router.push(`/quizzes/${quiz.id}`)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate quiz')
    },
  })

  const handleGenerate = () => {
    if (!selectedTopic) {
      toast.error('Please select a topic first')
      return
    }
    generateMutation.mutate()
  }

  const selectedQuizOption = QUIZ_OPTIONS.find((opt) => opt.questions === numQuestions)

  if (!student) {
    return null
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

          <h1 className="text-3xl font-bold text-gray-900">Start New Quiz</h1>
          <p className="mt-2 text-sm text-gray-600">
            Create a timed quiz to test your knowledge
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-2xl">
          <div className="rounded-xl border border-gray-200 bg-white p-8">
            <div className="space-y-6">
              {/* Subject Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Select Subject
                </label>
                <select
                  value={selectedSubject}
                  onChange={(e) => {
                    setSelectedSubject(e.target.value)
                    setSelectedTopic('')
                  }}
                  className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a subject...</option>
                  {subjects?.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Topic Selection */}
              {selectedSubject && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Select Topic
                  </label>
                  <select
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    className="mt-2 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Choose a topic...</option>
                    {topics?.map((topic) => (
                      <option key={topic.id} value={topic.id}>
                        {topic.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Difficulty Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Difficulty Level
                </label>
                <div className="mt-2 flex gap-3">
                  {DIFFICULTY_LEVELS.map((level) => (
                    <button
                      key={level.value}
                      onClick={() => setDifficulty(level.value)}
                      className={`flex-1 rounded-lg px-4 py-3 text-sm font-medium transition ${
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

              {/* Quiz Size Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Quiz Size & Duration
                </label>
                <div className="mt-2 grid grid-cols-2 gap-3">
                  {QUIZ_OPTIONS.map((option) => (
                    <button
                      key={option.questions}
                      onClick={() => setNumQuestions(option.questions)}
                      className={`rounded-lg border-2 p-4 text-left transition ${
                        numQuestions === option.questions
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">
                            {option.questions} Questions
                          </p>
                          <p className="mt-1 flex items-center gap-1 text-sm text-gray-600">
                            <Timer className="h-3 w-3" />
                            {option.duration} minutes
                          </p>
                        </div>
                        {numQuestions === option.questions && (
                          <div className="h-5 w-5 rounded-full bg-blue-600 flex items-center justify-center">
                            <svg className="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Preview Info */}
              {selectedTopic && selectedQuizOption && (
                <div className="rounded-lg bg-blue-50 p-4">
                  <div className="flex items-start gap-3">
                    <Timer className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-600" />
                    <div className="text-sm text-blue-900">
                      <p className="font-medium">Timed Quiz</p>
                      <p className="mt-1 text-blue-700">
                        You'll have {selectedQuizOption.duration} minutes to answer{' '}
                        {selectedQuizOption.questions} {difficulty} difficulty questions.
                        The quiz will auto-submit when time runs out.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!selectedTopic || generateMutation.isPending}
                className="w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              >
                {generateMutation.isPending ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Generating Quiz...
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-2">
                    <Timer className="h-5 w-5" />
                    Start Quiz
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
