import apiClient from './client'

export interface QuizQuestion {
  question_number: number
  type: string // MCQ, True/False
  question: string
  options?: string[]
  correct_answer?: string
  points: number
}

export interface Quiz {
  id: string
  student_id: string
  topic_id: string
  title: string
  difficulty: string
  total_questions: number
  duration_minutes: number
  max_score: number
  questions: QuizQuestion[]
  created_at: string
  updated_at: string
}

export interface QuizListItem {
  id: string
  title: string
  topic_id: string
  topic_name: string
  difficulty: string
  total_questions: number
  duration_minutes: number
  max_score: number
  created_at: string
  total_attempts: number
  best_score?: number
  latest_score?: number
}

export interface GradedQuizAnswer {
  question_number: number
  question: string
  student_answer: string
  correct_answer: string
  score: number
  is_correct: boolean
  feedback: string
}

export interface ImprovementData {
  is_first_attempt: boolean
  improvement: number
  best_score: number
  average_score: number
  total_attempts: number
  is_best_score?: boolean
}

export interface QuizAttempt {
  id: string
  quiz_id: string
  student_id: string
  started_at: string
  submitted_at?: string
  answers: Record<string, string>
  score?: number
  max_score?: number
  percentage?: number
  graded_answers?: GradedQuizAnswer[]
  passed?: boolean
  time_taken_seconds?: number
  time_exceeded?: boolean
  improvement_data?: ImprovementData
  created_at: string
  updated_at: string
}

export interface QuizStats {
  quiz_id: string
  total_attempts: number
  best_score: number
  average_score: number
  latest_score: number
  improvement_trend: number
  average_time_seconds: number
}

export interface GenerateQuizRequest {
  topic_id: string
  num_questions?: number
  difficulty?: 'easy' | 'medium' | 'hard'
}

export const quizzesApi = {
  // Generate a new quiz
  generate: async (request: GenerateQuizRequest): Promise<Quiz> => {
    return apiClient.post('/api/v1/quizzes/generate', {
      topic_id: request.topic_id,
      num_questions: request.num_questions || 10,
      difficulty: request.difficulty || 'medium',
    })
  },

  // Get all quizzes
  list: async (topicId?: string, limit: number = 20): Promise<QuizListItem[]> => {
    const params = new URLSearchParams()
    if (topicId) params.append('topic_id', topicId)
    params.append('limit', limit.toString())

    return apiClient.get(`/api/v1/quizzes?${params.toString()}`)
  },

  // Get a specific quiz
  get: async (quizId: string): Promise<Quiz> => {
    return apiClient.get(`/api/v1/quizzes/${quizId}`)
  },

  // Start a quiz attempt
  startAttempt: async (quizId: string): Promise<QuizAttempt> => {
    return apiClient.post(`/api/v1/quizzes/${quizId}/start`, {})
  },

  // Submit quiz answers
  submit: async (
    quizId: string,
    attemptId: string,
    answers: Record<string, string>
  ): Promise<QuizAttempt> => {
    return apiClient.post(`/api/v1/quizzes/${quizId}/submit`, {
      attempt_id: attemptId,
      answers,
    })
  },

  // Get all attempts for a quiz
  getAttempts: async (quizId: string): Promise<QuizAttempt[]> => {
    return apiClient.get(`/api/v1/quizzes/${quizId}/attempts`)
  },

  // Get quiz statistics
  getStats: async (quizId: string): Promise<QuizStats> => {
    return apiClient.get(`/api/v1/quizzes/${quizId}/stats`)
  },
}
