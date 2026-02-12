import apiClient from './client'

export interface StudentAnalytics {
  total_learning_time_minutes: number
  topics_studied: number
  topics_completed: number
  average_quiz_score: number
  average_worksheet_score: number
  weekly_time_minutes: number
  weekly_sessions: number
  overall_progress: number
}

export interface SubjectBreakdown {
  subject: string
  topics_studied: number
  topics_mastered: number
  average_mastery: number
  progress_percentage: number
}

export interface WeakArea {
  topic_id: string
  topic_name: string
  subject: string | null
  mastery_score: number
  reasons: string[]
  priority: number
}

export interface MasteryComponents {
  quiz_score: number
  worksheet_score: number
  consistency: number
  retention: number
}

export interface MasteryAttempts {
  quizzes: number
  worksheets: number
  sessions: number
}

export interface TopicMastery {
  topic_id: string
  mastery_score: number
  mastery_level: string
  components: MasteryComponents
  attempts: MasteryAttempts
  error: string | null
}

export interface ProgressRecord {
  id: string
  student_id: string
  topic_id: string
  mastery_level: number
  total_time_spent_seconds: number
  quiz_count: number
  worksheet_count: number
  average_quiz_score: number
  average_worksheet_score: number
  last_practiced_at: string | null
  created_at: string
  updated_at: string
}

export const progressApi = {
  getAnalytics: async (): Promise<StudentAnalytics> => {
    return apiClient.get('/api/v1/progress/analytics')
  },

  getSubjectBreakdown: async (): Promise<SubjectBreakdown[]> => {
    return apiClient.get('/api/v1/progress/subject-breakdown')
  },

  getWeakAreas: async (limit?: number): Promise<WeakArea[]> => {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())
    const query = params.toString()
    return apiClient.get(`/api/v1/progress/weak-areas${query ? `?${query}` : ''}`)
  },

  getTopicMastery: async (topicId: string): Promise<TopicMastery> => {
    return apiClient.get(`/api/v1/progress/topics/${topicId}/mastery`)
  },

  updateTopicProgress: async (topicId: string): Promise<ProgressRecord> => {
    return apiClient.post(`/api/v1/progress/topics/${topicId}/update`)
  },

  getRecords: async (subject?: string, completedOnly?: boolean): Promise<ProgressRecord[]> => {
    const params = new URLSearchParams()
    if (subject) params.append('subject', subject)
    if (completedOnly !== undefined) params.append('completed_only', completedOnly.toString())
    const query = params.toString()
    return apiClient.get(`/api/v1/progress/records${query ? `?${query}` : ''}`)
  },
}
