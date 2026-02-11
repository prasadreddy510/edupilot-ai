# EduPilot AI - Architecture Documentation

## Overview

EduPilot AI is a full-stack web application built with a modern, scalable architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│              (Next.js 14 + TypeScript + Tailwind)           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Student │  │  Parent  │  │   Auth   │  │  Shared  │   │
│  │   Pages  │  │  Pages   │  │  Pages   │  │Components│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          State Management (Zustand)                   │  │
│  │          API Client (Axios + React Query)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                           │
│                  (FastAPI + Python 3.11)                    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │ Students │  │Worksheets│  │  Quizzes │   │
│  │   API    │  │   API    │  │   API    │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Business Logic Layer                    │  │
│  │  • AI Service (Claude)                               │  │
│  │  • RAG Service (LangChain + Chroma)                  │  │
│  │  • Worksheet Generator                               │  │
│  │  • Grading Engine                                    │  │
│  │  • Analytics Calculator                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │  Chroma DB   │     │
│  │  (Primary)   │  │  (Cache)     │  │  (Vectors)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Services                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Firebase   │  │  Claude AI   │  │  HuggingFace │     │
│  │    (Auth)    │  │  (LLM API)   │  │ (Embeddings) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Authentication Flow
1. User enters phone number in frontend
2. Firebase sends OTP to phone
3. User verifies OTP
4. Frontend sends OTP token to backend
5. Backend verifies with Firebase Admin SDK
6. Backend generates JWT token
7. Frontend stores JWT and uses for subsequent requests

### AI-Powered Learning Flow
1. Student selects topic
2. Frontend requests explanation from backend
3. Backend retrieves relevant NCERT content from Chroma (RAG)
4. Backend sends context + query to Claude API
5. Claude generates personalized explanation
6. Backend returns explanation to frontend
7. Session tracked in PostgreSQL

### Worksheet Generation Flow
1. Student requests worksheet for topic
2. Backend generates questions (70% template, 30% AI)
3. Worksheet saved to PostgreSQL
4. Student answers questions
5. Backend grades using multi-tier system:
   - Tier 1: Deterministic (exact match)
   - Tier 2: Pattern-based (regex)
   - Tier 3: AI-based (Claude evaluation)
6. Results saved and shown to student

### Progress Tracking Flow
1. Background job calculates mastery levels
2. Aggregates quiz scores, worksheet scores, time spent
3. Identifies weak areas (mastery < 60%)
4. Updates progress records
5. Parent dashboard queries aggregated data
6. Generates visualizations and reports

## Database Schema

See [DATABASE.md](./DATABASE.md) for detailed schema documentation.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/verify-otp` - Verify OTP
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Students
- `GET /api/v1/students/me` - Get student profile
- `GET /api/v1/subjects` - List subjects by grade
- `GET /api/v1/topics/{subject_id}` - List topics
- `POST /api/v1/topics/{id}/explain` - Get AI explanation

### Worksheets
- `POST /api/v1/worksheets/generate` - Generate worksheet
- `GET /api/v1/worksheets` - List worksheets
- `POST /api/v1/worksheets/{id}/submit` - Submit answers
- `GET /api/v1/worksheets/{id}/result` - Get graded result

### Quizzes
- `GET /api/v1/quizzes` - List available quizzes
- `POST /api/v1/quizzes/{id}/start` - Start quiz attempt
- `POST /api/v1/quizzes/{id}/submit` - Submit quiz

### Doubts
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations/{id}/messages` - Send message

### Progress
- `GET /api/v1/progress/me` - Get student progress
- `GET /api/v1/progress/weak-areas` - Get weak areas

### Parents
- `GET /api/v1/parents/students` - List linked students
- `GET /api/v1/parents/analytics/{student_id}` - Get analytics
- `GET /api/v1/parents/report/{student_id}` - Download report

## Security

- Firebase Authentication for phone-based OTP
- JWT tokens for API authentication
- CORS protection
- Rate limiting on sensitive endpoints
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (input sanitization)
- HTTPS in production

## Performance Optimization

- Redis caching for AI responses
- Database connection pooling
- Lazy loading of images
- Code splitting in frontend
- Background jobs for heavy computations
- Database indexing on frequently queried fields

## Scalability

- Stateless backend (horizontal scaling)
- Database read replicas (future)
- CDN for static assets (future)
- Load balancer (production)
- Microservices architecture (future expansion)

## Monitoring & Observability

- Application logs (Python logging)
- Error tracking (Sentry)
- Performance monitoring
- Database query monitoring
- API response time tracking
