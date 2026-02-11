# EduPilot AI

> An AI-powered educational platform for Indian students (Grades 3-10) with intelligent learning, worksheet generation, quizzes, doubt chatbot, and parent progress tracking.

## Features

- **AI-Powered Learning**: Context-aware explanations using Claude AI and NCERT curriculum
- **Smart Worksheets**: Generate practice worksheets with auto-grading
- **Interactive Quizzes**: Timed assessments with instant feedback
- **Doubt Chatbot**: RAG-based AI chatbot for clearing student doubts
- **Progress Tracking**: Intelligent mastery level calculation and weak area identification
- **Parent Dashboard**: Comprehensive analytics and progress reports

## Tech Stack

### Frontend
- Next.js 14 (App Router) with TypeScript
- Tailwind CSS + Shadcn UI
- Zustand (State Management)
- TanStack Query (Data Fetching)
- Firebase Authentication (Client)
- Recharts (Visualizations)
- KaTeX (Math Rendering)

### Backend
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 + Alembic
- PostgreSQL
- Redis (Caching)
- Firebase Admin SDK (Authentication)
- Anthropic Claude API (AI)
- LangChain + Chroma (RAG)
- Celery (Background Tasks)

## Project Structure

```
edupilot-ai/
├── frontend/           # Next.js application
├── backend/            # FastAPI application
├── docker-compose.yml  # Local development environment
└── .github/workflows/  # CI/CD pipelines
```

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 14+ (or use Docker)
- Redis 7+ (or use Docker)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd edupilot-ai
```

### 2. Set up environment variables

#### Backend (.env)

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://edupilot:edupilot_dev_password@localhost:5432/edupilot

# Redis
REDIS_URL=redis://localhost:6379/0

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Claude AI
ANTHROPIC_API_KEY=your_claude_api_key_here

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

#### Frontend (.env.local)

```bash
cd frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### 3. Start with Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend (port 3000)

Visit http://localhost:3000

### 4. Manual Setup (Alternative)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

Backend will run at http://localhost:8000

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at http://localhost:3000

## Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `pytest` (backend) and `npm test` (frontend)
4. Commit with conventional commits: `git commit -m "feat: add new feature"`
5. Push and create a pull request

## Project Phases

- [x] Phase 1: Project Scaffolding
- [ ] Phase 2: Database Schema & Models
- [ ] Phase 3: Authentication System
- [ ] Phase 4: AI Services Foundation
- [ ] Phase 5: Student Learning Module
- [ ] Phase 6: Worksheet Generation
- [ ] Phase 7: Auto-Grading System
- [ ] Phase 8: Quiz System
- [ ] Phase 9: Doubt Chatbot
- [ ] Phase 10: Progress Tracking
- [ ] Phase 11: Parent Dashboard
- [ ] Phase 12: Polish & Optimization

## Architecture Overview

### Authentication Flow
1. User enters phone number
2. Firebase sends OTP
3. User verifies OTP
4. Backend generates JWT token
5. Token used for API authentication

### RAG System
1. NCERT textbooks embedded and stored in Chroma DB
2. User questions trigger vector similarity search
3. Top-k relevant chunks retrieved
4. Claude generates answer with context
5. Source attribution included

### Grading System
- **Tier 1**: Deterministic (MCQ, True/False) - Exact match
- **Tier 2**: Pattern-based (Numerical) - Regex + tolerance
- **Tier 3**: AI-based (Short answer) - Claude evaluation

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- NCERT for educational content
- Anthropic for Claude AI
- Firebase for authentication services
