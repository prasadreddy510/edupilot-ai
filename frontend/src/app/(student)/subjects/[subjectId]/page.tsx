'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api/client'
import { ArrowLeft, BookOpen, ChevronRight, Clock, Star } from 'lucide-react'
import { Subject, Topic } from '@/types'

export default function SubjectDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()
  const subjectId = params.subjectId as string

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch subject details
  const { data: subject, isLoading: subjectLoading } = useQuery<Subject>({
    queryKey: ['subject', subjectId],
    queryFn: async () => {
      return apiClient.get(`/api/v1/subjects/${subjectId}`)
    },
    enabled: !!subjectId,
  })

  // Fetch topics for this subject
  const { data: topics, isLoading: topicsLoading } = useQuery<Topic[]>({
    queryKey: ['topics', subjectId],
    queryFn: async () => {
      return apiClient.get(`/api/v1/topics?subject_id=${subjectId}`)
    },
    enabled: !!subjectId,
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

          {subjectLoading ? (
            <div className="h-8 w-64 animate-pulse rounded bg-gray-200" />
          ) : subject ? (
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{subject.name}</h1>
              <p className="mt-2 text-gray-600">
                Grade {subject.grade} • {topics?.length || 0} Topics
              </p>
            </div>
          ) : (
            <h1 className="text-3xl font-bold text-gray-900">Subject</h1>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Topics List */}
        <section>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Topics to Learn</h2>
            <p className="mt-1 text-sm text-gray-600">
              Click on any topic to start learning
            </p>
          </div>

          {topicsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="h-24 animate-pulse rounded-xl bg-gray-200"
                />
              ))}
            </div>
          ) : topics && topics.length > 0 ? (
            <div className="space-y-4">
              {topics.map((topic, index) => (
                <TopicCard
                  key={topic.id}
                  topic={topic}
                  index={index}
                  subjectId={subjectId}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900">
                No topics available
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                Topics for this subject will appear here.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

function TopicCard({
  topic,
  index,
  subjectId,
}: {
  topic: Topic
  index: number
  subjectId: string
}) {
  // Mock data - in real app, fetch from progress API
  const isCompleted = index < 2
  const isInProgress = index === 2

  return (
    <Link
      href={`/student/learn/${topic.id}`}
      className="group block rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
    >
      <div className="flex items-start gap-4">
        {/* Order Number */}
        <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-blue-100 text-lg font-bold text-blue-600">
          {topic.order || index + 1}
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600">
                {topic.name}
              </h3>
              {topic.description && (
                <p className="mt-1 text-sm text-gray-600">{topic.description}</p>
              )}
            </div>
            <ChevronRight className="h-5 w-5 flex-shrink-0 text-gray-400 transition group-hover:translate-x-1 group-hover:text-blue-600" />
          </div>

          {/* Progress indicators */}
          <div className="mt-4 flex items-center gap-4">
            {isCompleted && (
              <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                <Star className="h-3 w-3 fill-current" />
                Completed
              </span>
            )}
            {isInProgress && (
              <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-700">
                <Clock className="h-3 w-3" />
                In Progress
              </span>
            )}
            {!isCompleted && !isInProgress && (
              <span className="text-xs text-gray-500">Not started</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
