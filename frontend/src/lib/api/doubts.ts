import apiClient from './client'

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  metadata?: {
    sources?: Source[]
    has_context?: boolean
  }
  created_at: string
  updated_at: string
}

export interface Source {
  text: string
  metadata: {
    grade?: number
    subject?: string
    chapter?: string
    page?: number
  }
}

export interface Conversation {
  id: string
  student_id: string
  topic_id?: string
  title: string
  subject?: string
  created_at: string
  updated_at: string
}

export interface ConversationListItem {
  id: string
  student_id: string
  topic_id?: string
  topic_name?: string
  title: string
  subject?: string
  message_count: number
  last_message?: string
  last_message_at?: string
  created_at: string
  updated_at: string
}

export interface ChatResponse {
  user_message: Message
  assistant_message: Message
  sources: Source[]
}

export interface CreateConversationRequest {
  title: string
  topic_id?: string
  subject?: string
}

export interface SendMessageRequest {
  content: string
  topic?: string
  subject?: string
}

export const doubtsApi = {
  // Create a new conversation
  createConversation: async (data: CreateConversationRequest): Promise<Conversation> => {
    return apiClient.post('/api/v1/doubts/conversations', data)
  },

  // Get all conversations
  listConversations: async (
    topicId?: string,
    subject?: string,
    search?: string,
    limit: number = 20
  ): Promise<ConversationListItem[]> => {
    const params = new URLSearchParams()
    if (topicId) params.append('topic_id', topicId)
    if (subject) params.append('subject', subject)
    if (search) params.append('search', search)
    params.append('limit', limit.toString())

    return apiClient.get(`/api/v1/doubts/conversations?${params.toString()}`)
  },

  // Get a specific conversation
  getConversation: async (conversationId: string): Promise<Conversation> => {
    return apiClient.get(`/api/v1/doubts/conversations/${conversationId}`)
  },

  // Get messages in a conversation
  getMessages: async (conversationId: string, limit: number = 50): Promise<Message[]> => {
    return apiClient.get(
      `/api/v1/doubts/conversations/${conversationId}/messages?limit=${limit}`
    )
  },

  // Send a message in a conversation
  sendMessage: async (
    conversationId: string,
    content: string
  ): Promise<ChatResponse> => {
    return apiClient.post(`/api/v1/doubts/conversations/${conversationId}/messages`, {
      content,
    })
  },

  // Delete a conversation
  deleteConversation: async (conversationId: string): Promise<void> => {
    return apiClient.delete(`/api/v1/doubts/conversations/${conversationId}`)
  },

  // Quick ask (no conversation)
  quickAsk: async (data: SendMessageRequest): Promise<ChatResponse> => {
    return apiClient.post('/api/v1/doubts/quick-ask', data)
  },
}
