import apiClient from './client'

export interface LearningSession {
  id: string
  student_id: string
  topic_id: string
  start_time: string
  end_time?: string
  duration_minutes?: number
  completed: boolean
  created_at: string
  updated_at: string
}

export interface LearningSessionStats {
  total_sessions: number
  total_time_minutes: number
  sessions_this_week: number
  time_this_week_minutes: number
  unique_topics_learned: number
}

export const learningApi = {
  // Start a new learning session
  startSession: async (topicId: string): Promise<LearningSession> => {
    return apiClient.post('/api/v1/learning/sessions', {
      topic_id: topicId,
    })
  },

  // End a learning session
  endSession: async (
    sessionId: string,
    completed: boolean = false
  ): Promise<LearningSession> => {
    return apiClient.patch(`/api/v1/learning/sessions/${sessionId}`, {
      completed,
    })
  },

  // Get learning sessions
  getSessions: async (topicId?: string, limit: number = 20): Promise<LearningSession[]> => {
    const params = new URLSearchParams()
    if (topicId) params.append('topic_id', topicId)
    params.append('limit', limit.toString())

    return apiClient.get(`/api/v1/learning/sessions?${params.toString()}`)
  },

  // Get a specific session
  getSession: async (sessionId: string): Promise<LearningSession> => {
    return apiClient.get(`/api/v1/learning/sessions/${sessionId}`)
  },

  // Get learning statistics
  getStats: async (): Promise<LearningSessionStats> => {
    return apiClient.get('/api/v1/learning/sessions/stats')
  },
}
