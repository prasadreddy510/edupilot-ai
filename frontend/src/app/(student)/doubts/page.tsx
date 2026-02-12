'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { doubtsApi, ConversationListItem } from '@/lib/api/doubts'
import {
  ArrowLeft,
  MessageCircle,
  Plus,
  Search,
  Trash2,
  Loader2,
} from 'lucide-react'
import { toast } from 'sonner'

export default function DoubtsPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { isAuthenticated, student } = useAuthStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [newConvTitle, setNewConvTitle] = useState('')
  const [showNewConvDialog, setShowNewConvDialog] = useState(false)

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch conversations
  const { data: conversations, isLoading } = useQuery<ConversationListItem[]>({
    queryKey: ['conversations', searchQuery],
    queryFn: () => doubtsApi.listConversations(undefined, undefined, searchQuery, 50),
    enabled: !!student,
  })

  // Create conversation mutation
  const createMutation = useMutation({
    mutationFn: async () => {
      if (!newConvTitle.trim()) {
        throw new Error('Please enter a title')
      }
      return doubtsApi.createConversation({ title: newConvTitle.trim() })
    },
    onSuccess: (conversation) => {
      toast.success('Conversation created!')
      setNewConvTitle('')
      setShowNewConvDialog(false)
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      router.push(`/doubts/${conversation.id}`)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create conversation')
    },
  })

  // Delete conversation mutation
  const deleteMutation = useMutation({
    mutationFn: async (conversationId: string) => {
      return doubtsApi.deleteConversation(conversationId)
    },
    onSuccess: () => {
      toast.success('Conversation deleted')
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: () => {
      toast.error('Failed to delete conversation')
    },
  })

  const handleDelete = (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteMutation.mutate(conversationId)
    }
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
            href="/dashboard"
            className="mb-4 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Ask a Doubt</h1>
              <p className="mt-2 text-sm text-gray-600">
                Get instant help from your AI tutor
              </p>
            </div>

            <button
              onClick={() => setShowNewConvDialog(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              New Conversation
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl">
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-gray-300 pl-10 pr-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Conversations List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : conversations && conversations.length > 0 ? (
            <div className="space-y-4">
              {conversations.map((conversation) => (
                <ConversationCard
                  key={conversation.id}
                  conversation={conversation}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
              <MessageCircle className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900">
                No conversations yet
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                Start a conversation to ask your doubts
              </p>
              <button
                onClick={() => setShowNewConvDialog(true)}
                className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
              >
                <Plus className="h-4 w-4" />
                New Conversation
              </button>
            </div>
          )}
        </div>
      </main>

      {/* New Conversation Dialog */}
      {showNewConvDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6">
            <h2 className="text-xl font-bold text-gray-900">New Conversation</h2>
            <p className="mt-2 text-sm text-gray-600">
              Give your conversation a title
            </p>

            <input
              type="text"
              placeholder="e.g., Help with Fractions"
              value={newConvTitle}
              onChange={(e) => setNewConvTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  createMutation.mutate()
                }
              }}
              className="mt-4 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => {
                  setShowNewConvDialog(false)
                  setNewConvTitle('')
                }}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 transition hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => createMutation.mutate()}
                disabled={!newConvTitle.trim() || createMutation.isPending}
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
              >
                {createMutation.isPending ? (
                  <span className="inline-flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Creating...
                  </span>
                ) : (
                  'Create'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ConversationCard({
  conversation,
  onDelete,
}: {
  conversation: ConversationListItem
  onDelete: (e: React.MouseEvent, id: string) => void
}) {
  const router = useRouter()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div
      onClick={() => router.push(`/doubts/${conversation.id}`)}
      className="group cursor-pointer rounded-xl border border-gray-200 bg-white p-6 transition hover:shadow-lg"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-100 p-2">
              <MessageCircle className="h-5 w-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 group-hover:text-blue-600">
                {conversation.title}
              </h3>
              {conversation.last_message && (
                <p className="mt-1 text-sm text-gray-600 line-clamp-1">
                  {conversation.last_message}
                </p>
              )}
            </div>
          </div>

          <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
            <span>{conversation.message_count} messages</span>
            {conversation.last_message_at && (
              <span>{formatDate(conversation.last_message_at)}</span>
            )}
            {conversation.subject && (
              <span className="rounded-full bg-gray-100 px-2 py-1 text-xs">
                {conversation.subject}
              </span>
            )}
          </div>
        </div>

        <button
          onClick={(e) => onDelete(e, conversation.id)}
          className="rounded-lg p-2 text-gray-400 transition hover:bg-red-50 hover:text-red-600"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
