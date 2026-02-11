import Link from 'next/link'
import { ArrowRight, BookOpen, Brain, BarChart, MessageCircle } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">EduPilot AI</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            AI-Powered Learning for
            <span className="block text-blue-600">Indian Students</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
            Personalized education aligned with NCERT curriculum. Smart worksheets, interactive
            quizzes, and AI-powered doubt clearing for Grades 3-10.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              href="/register"
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-base font-medium text-white hover:bg-blue-700"
            >
              Start Learning Free
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="/about"
              className="rounded-lg border border-gray-300 px-6 py-3 text-base font-medium text-gray-700 hover:bg-gray-50"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold text-gray-900">
          Everything You Need to Excel
        </h2>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <FeatureCard
            icon={<Brain className="h-8 w-8 text-blue-600" />}
            title="AI Explanations"
            description="Context-aware explanations using NCERT curriculum and Claude AI"
          />
          <FeatureCard
            icon={<BookOpen className="h-8 w-8 text-green-600" />}
            title="Smart Worksheets"
            description="Generate practice worksheets with instant auto-grading"
          />
          <FeatureCard
            icon={<MessageCircle className="h-8 w-8 text-purple-600" />}
            title="Doubt Chatbot"
            description="24/7 AI tutor to clear all your subject doubts"
          />
          <FeatureCard
            icon={<BarChart className="h-8 w-8 text-orange-600" />}
            title="Progress Tracking"
            description="Detailed analytics and parent dashboard with reports"
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="rounded-2xl bg-blue-600 px-6 py-16 text-center text-white">
          <h2 className="text-3xl font-bold">Ready to Transform Your Learning?</h2>
          <p className="mt-4 text-lg text-blue-100">
            Join thousands of students already learning smarter with EduPilot AI
          </p>
          <Link
            href="/register"
            className="mt-8 inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-base font-medium text-blue-600 hover:bg-blue-50"
          >
            Get Started Now
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-8">
          <p className="text-center text-sm text-gray-600">
            © 2024 EduPilot AI. Built for Indian students, aligned with NCERT curriculum.
          </p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
      <div className="mb-4">{icon}</div>
      <h3 className="mb-2 text-lg font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  )
}
