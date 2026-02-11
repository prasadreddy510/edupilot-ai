'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/lib/store/authStore'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { doubtsApi, Message, Conversation, Source } from '@/lib/api/doubts'
import {
  ArrowLeft,
  Send,
  Loader2,
  BookOpen,
  Sparkles,
} from 'lucide-react'
import { toast } from 'sonner'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { isAuthenticated, student } = useAuthStore()
  const conversationId = params.id as string

  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated || !student) {
      router.push('/login')
    }
  }, [isAuthenticated, student, router])

  // Fetch conversation
  const { data: conversation } = useQuery<Conversation>({
    queryKey: ['conversation', conversationId],
    queryFn: () => doubtsApi.getConversation(conversationId),
    enabled: !!conversationId,
  })

  // Fetch messages
  const { data: messages, isLoading } = useQuery<Message[]>({
    queryKey: ['messages', conversationId],
    queryFn: () => doubtsApi.getMessages(conversationId),
    enabled: !!conversationId,
    refetchInterval: false, // Manual refetch after sending
  })

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: async () => {
      const content = inputMessage.trim()
      if (!content) throw new Error('Message cannot be empty')
      return doubtsApi.sendMessage(conversationId, content)
    },
    onMutate: () => {
      setIsTyping(true)
    },
    onSuccess: () => {
      setInputMessage('')
      setIsTyping(false)
      queryClient.invalidateQueries({ queryKey: ['messages', conversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
    onError: (error: any) => {
      setIsTyping(false)
      toast.error(error.message || 'Failed to send message')
    },
  })

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (inputMessage.trim() && !sendMutation.isPending) {
      sendMutation.mutate()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!student) {
    return null
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white px-4 py-4">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/student/doubts"
              className="rounded-lg p-2 text-gray-600 transition hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                {conversation?.title || 'Loading...'}
              </h1>
              <p className="text-sm text-gray-500">AI Tutor</p>
            </div>
          </div>

          {conversation?.subject && (
            <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
              {conversation.subject}
            </span>
          )}
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="container mx-auto max-w-3xl space-y-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : messages && messages.length > 0 ? (
            <>
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isTyping && (
                <div className="flex items-start gap-3">
                  <div className="rounded-full bg-blue-600 p-2">
                    <Sparkles className="h-4 w-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="inline-block rounded-2xl bg-gray-100 px-4 py-3">
                      <div className="flex gap-1">
                        <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '0ms' }} />
                        <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '150ms' }} />
                        <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto mb-4 rounded-full bg-blue-100 p-4 w-fit">
                <Sparkles className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                Start the conversation
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                Ask any question and get instant help from your AI tutor
              </p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-white px-4 py-4">
        <div className="container mx-auto max-w-3xl">
          <div className="flex items-end gap-3">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your question here..."
              rows={1}
              className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{
                minHeight: '52px',
                maxHeight: '200px',
                height: 'auto',
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = 'auto'
                target.style.height = target.scrollHeight + 'px'
              }}
            />
            <button
              onClick={handleSend}
              disabled={!inputMessage.trim() || sendMutation.isPending}
              className="rounded-lg bg-blue-600 p-3 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  const sources = message.metadata?.sources || []

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 rounded-full p-2 ${
          isUser ? 'bg-gray-200' : 'bg-blue-600'
        }`}
      >
        {isUser ? (
          <div className="h-4 w-4 font-bold text-gray-700">U</div>
        ) : (
          <Sparkles className="h-4 w-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`inline-block max-w-[85%] rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                  p: ({ children }) => (
                    <p className="my-2 leading-relaxed text-gray-900">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="my-2 ml-4 list-disc text-gray-900">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="my-2 ml-4 list-decimal text-gray-900">{children}</ol>
                  ),
                  code: ({ inline, children, ...props }: any) =>
                    inline ? (
                      <code
                        className="rounded bg-gray-200 px-1 py-0.5 text-sm font-mono text-gray-800"
                        {...props}
                      >
                        {children}
                      </code>
                    ) : (
                      <code
                        className="block rounded-lg bg-gray-800 p-3 text-sm text-gray-100"
                        {...props}
                      >
                        {children}
                      </code>
                    ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-gray-900">{children}</strong>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Sources */}
        {!isUser && sources.length > 0 && (
          <div className="mt-2 space-y-1">
            {sources.map((source: Source, index: number) => (
              <div
                key={index}
                className="flex items-start gap-2 rounded-lg bg-blue-50 p-2 text-xs"
              >
                <BookOpen className="mt-0.5 h-3 w-3 flex-shrink-0 text-blue-600" />
                <div>
                  <p className="text-blue-900">
                    {source.metadata.subject && `${source.metadata.subject} - `}
                    {source.metadata.chapter && source.metadata.chapter}
                    {source.metadata.page && ` (Page ${source.metadata.page})`}
                  </p>
                  <p className="mt-1 text-blue-700">{source.text}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="mt-1 text-xs text-gray-500">
          {new Date(message.created_at).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  )
}
