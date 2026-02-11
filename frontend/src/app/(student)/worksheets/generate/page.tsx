'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '@/lib/api/client'
import { worksheetsApi } from '@/lib/api/worksheets'
import { Subject, Topic } from '@/types'
import { ArrowLeft, Loader2, Sparkles } from 'lucide-react'
import { toast } from 'sonner'

const DIFFICULTY_LEVELS = [
  { value: 'easy', label: 'Easy', color: 'bg-green-100 text-green-700 hover:bg-green-200' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' },
  { value: 'hard', label: 'Hard', color: 'bg-red-100 text-red-700 hover:bg-red-200' },
]

const QUESTION_COUNTS = [5, 10, 15, 20]

export default function GenerateWorksheetPage() {
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

  // Generate worksheet mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      if (!selectedTopic) {
        throw new Error('Please select a topic')
      }

      return worksheetsApi.generate({
        topic_id: selectedTopic,
        num_questions: numQuestions,
        difficulty: difficulty as 'easy' | 'medium' | 'hard',
      })
    },
    onSuccess: (worksheet) => {
      toast.success('Worksheet generated successfully!')
      router.push(`/student/worksheets/${worksheet.id}`)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate worksheet')
    },
  })

  const handleGenerate = () => {
    if (!selectedTopic) {
      toast.error('Please select a topic first')
      return
    }
    generateMutation.mutate()
  }

  if (!student) {
    return null
  }

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

          <h1 className="text-3xl font-bold text-gray-900">Generate Worksheet</h1>
          <p className="mt-2 text-sm text-gray-600">
            Create a custom practice worksheet with AI-generated questions
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

              {/* Number of Questions */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Number of Questions
                </label>
                <div className="mt-2 grid grid-cols-4 gap-3">
                  {QUESTION_COUNTS.map((count) => (
                    <button
                      key={count}
                      onClick={() => setNumQuestions(count)}
                      className={`rounded-lg px-4 py-3 text-sm font-medium transition ${
                        numQuestions === count
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {count}
                    </button>
                  ))}
                </div>
              </div>

              {/* Preview Info */}
              {selectedTopic && (
                <div className="rounded-lg bg-blue-50 p-4">
                  <div className="flex items-start gap-3">
                    <Sparkles className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-600" />
                    <div className="text-sm text-blue-900">
                      <p className="font-medium">AI-Powered Generation</p>
                      <p className="mt-1 text-blue-700">
                        Your worksheet will contain {numQuestions} questions at{' '}
                        {difficulty} difficulty, with a mix of template-based (70%) and
                        AI-generated (30%) questions for best results.
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
                    Generating Worksheet...
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Generate Worksheet
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
