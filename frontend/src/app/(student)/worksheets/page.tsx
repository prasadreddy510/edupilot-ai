'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery } from '@tanstack/react-query'
import { worksheetsApi, WorksheetListItem } from '@/lib/api/worksheets'
import {
  ArrowLeft,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Plus,
} from 'lucide-react'

export default function WorksheetsPage() {
  const router = useRouter()
  const { isAuthenticated, student } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch worksheets
  const { data: worksheets, isLoading } = useQuery<WorksheetListItem[]>({
    queryKey: ['worksheets'],
    queryFn: () => worksheetsApi.list(undefined, 50),
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
            href="/student/dashboard"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Practice Worksheets</h1>
              <p className="mt-2 text-sm text-gray-600">
                Generate AI-powered worksheets to practice any topic
              </p>
            </div>

            <Link
              href="/student/worksheets/generate"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Generate New Worksheet
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
        ) : worksheets && worksheets.length > 0 ? (
          <div className="space-y-4">
            {worksheets.map((worksheet) => (
              <WorksheetCard key={worksheet.id} worksheet={worksheet} />
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              No worksheets yet
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Generate your first worksheet to start practicing
            </p>
            <Link
              href="/student/worksheets/generate"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              Generate Worksheet
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}

function WorksheetCard({ worksheet }: { worksheet: WorksheetListItem }) {
  const router = useRouter()

  const difficultyColors = {
    easy: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-700',
    hard: 'bg-red-100 text-red-700',
  }

  const handleClick = () => {
    if (worksheet.is_submitted) {
      // View results
      router.push(`/student/worksheets/${worksheet.id}/result`)
    } else {
      // Start worksheet
      router.push(`/student/worksheets/${worksheet.id}`)
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
              {worksheet.title}
            </h3>
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                difficultyColors[worksheet.difficulty as keyof typeof difficultyColors] ||
                'bg-gray-100 text-gray-700'
              }`}
            >
              {worksheet.difficulty}
            </span>
          </div>

          <p className="mt-1 text-sm text-gray-600">{worksheet.topic_name}</p>

          <div className="mt-4 flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>{worksheet.total_questions} questions</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>
                {new Date(worksheet.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </span>
            </div>
          </div>
        </div>

        <div className="ml-4 text-right">
          {worksheet.is_submitted ? (
            <div className="space-y-2">
              <div
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ${
                  worksheet.latest_percentage && worksheet.latest_percentage >= 60
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {worksheet.latest_percentage && worksheet.latest_percentage >= 60 ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <XCircle className="h-4 w-4" />
                )}
                {worksheet.latest_percentage?.toFixed(0)}%
              </div>
              <p className="text-xs text-gray-500">
                {worksheet.latest_score}/{worksheet.max_score} points
              </p>
            </div>
          ) : (
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700">
              <Loader2 className="h-4 w-4" />
              Not submitted
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
