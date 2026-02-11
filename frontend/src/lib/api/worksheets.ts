import apiClient from './client'

export interface Question {
  question_number: number
  type: string // MCQ, Short Answer, Numerical, True/False
  question: string
  options?: string[]
  correct_answer?: string
  points: number
}

export interface Worksheet {
  id: string
  student_id: string
  topic_id: string
  title: string
  difficulty: string
  total_questions: number
  max_score: number
  questions: Question[]
  created_at: string
  updated_at: string
}

export interface WorksheetListItem {
  id: string
  title: string
  topic_id: string
  topic_name: string
  difficulty: string
  total_questions: number
  max_score: number
  created_at: string
  is_submitted: boolean
  latest_score?: number
  latest_percentage?: number
}

export interface GradedAnswer {
  question_number: number
  question: string
  student_answer: string
  correct_answer: string
  score: number
  max_score: number
  feedback: string
  is_correct: boolean
}

export interface WorksheetSubmission {
  id: string
  worksheet_id: string
  student_id: string
  answers: Record<string, string>
  score: number
  max_score: number
  percentage: number
  graded_answers: GradedAnswer[]
  passed: boolean
  submitted_at: string
  created_at: string
  updated_at: string
}

export interface GenerateWorksheetRequest {
  topic_id: string
  num_questions?: number
  difficulty?: 'easy' | 'medium' | 'hard'
}

export const worksheetsApi = {
  // Generate a new worksheet
  generate: async (request: GenerateWorksheetRequest): Promise<Worksheet> => {
    return apiClient.post('/api/v1/worksheets/generate', {
      topic_id: request.topic_id,
      num_questions: request.num_questions || 10,
      difficulty: request.difficulty || 'medium',
    })
  },

  // Get all worksheets
  list: async (topicId?: string, limit: number = 20): Promise<WorksheetListItem[]> => {
    const params = new URLSearchParams()
    if (topicId) params.append('topic_id', topicId)
    params.append('limit', limit.toString())

    return apiClient.get(`/api/v1/worksheets?${params.toString()}`)
  },

  // Get a specific worksheet
  get: async (worksheetId: string): Promise<Worksheet> => {
    return apiClient.get(`/api/v1/worksheets/${worksheetId}`)
  },

  // Submit answers for a worksheet
  submit: async (
    worksheetId: string,
    answers: Record<string, string>
  ): Promise<WorksheetSubmission> => {
    return apiClient.post(`/api/v1/worksheets/${worksheetId}/submit`, {
      answers,
    })
  },

  // Get submissions for a worksheet
  getSubmissions: async (worksheetId: string): Promise<WorksheetSubmission[]> => {
    return apiClient.get(`/api/v1/worksheets/${worksheetId}/submissions`)
  },

  // Get latest submissions
  getLatestSubmissions: async (limit: number = 10): Promise<WorksheetSubmission[]> => {
    return apiClient.get(`/api/v1/worksheets/submissions/latest?limit=${limit}`)
  },
}
