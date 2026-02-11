/**
 * Shared TypeScript types for the application
 */

export interface User {
  id: string
  phone_number: string
  user_type: 'student' | 'parent'
  created_at: string
  updated_at: string
}

export interface Student {
  id: string
  user_id: string
  name: string
  grade: number
  email?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface Parent {
  id: string
  user_id: string
  name: string
  email?: string
  created_at: string
  updated_at: string
}

export interface Subject {
  id: string
  name: string
  grade: number
  description?: string
  icon?: string
}

export interface Topic {
  id: string
  subject_id: string
  name: string
  description?: string
  order: number
}

export interface Worksheet {
  id: string
  student_id: string
  topic_id: string
  title: string
  questions: Question[]
  created_at: string
  difficulty_level: 'easy' | 'medium' | 'hard'
}

export interface Question {
  id: string
  question_text: string
  question_type: 'mcq' | 'short_answer' | 'numerical' | 'true_false'
  options?: string[]
  correct_answer: string
  points: number
}

export interface WorksheetSubmission {
  id: string
  worksheet_id: string
  student_id: string
  answers: { [questionId: string]: string }
  score: number
  max_score: number
  feedback: { [questionId: string]: string }
  graded_at: string
  submitted_at: string
}

export interface Quiz {
  id: string
  topic_id: string
  title: string
  duration_minutes: number
  questions: Question[]
  total_points: number
  created_at: string
}

export interface QuizAttempt {
  id: string
  quiz_id: string
  student_id: string
  answers: { [questionId: string]: string }
  score: number
  max_score: number
  started_at: string
  submitted_at?: string
  time_taken_seconds: number
}

export interface Conversation {
  id: string
  student_id: string
  topic_id?: string
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  created_at: string
}

export interface ProgressRecord {
  id: string
  student_id: string
  topic_id: string
  mastery_level: number
  last_practiced_at: string
  total_time_spent_seconds: number
  quiz_count: number
  worksheet_count: number
}

export interface WeakArea {
  id: string
  student_id: string
  topic_id: string
  topic_name: string
  subject_name: string
  mastery_level: number
  identified_at: string
}

export interface AnalyticsSummary {
  total_time_spent_seconds: number
  subjects_studied: number
  worksheets_completed: number
  quizzes_taken: number
  average_score: number
  weak_topics: WeakArea[]
  improvement_trend: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
  student?: Student
  parent?: Parent
}
