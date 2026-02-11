# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+ (or use Docker)
- Redis 7+ (or use Docker)

### Initial Setup

Run the automated setup script:

```bash
./setup.sh
```

This will:
1. Check prerequisites
2. Create Python virtual environment
3. Install backend dependencies
4. Install frontend dependencies
5. Start PostgreSQL and Redis via Docker
6. Run database migrations
7. Create `.env` files from examples

### Environment Variables

#### Backend (.env)

```env
DATABASE_URL=postgresql://edupilot:edupilot_dev_password@localhost:5432/edupilot
REDIS_URL=redis://localhost:6379/0
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
ANTHROPIC_API_KEY=your_claude_api_key
SECRET_KEY=your_secret_key
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_domain
# ... other Firebase config
```

## Running the Application

### Option 1: Using Docker Compose (Recommended)

```bash
./start.sh
```

Or manually:

```bash
docker-compose up -d
```

### Option 2: Running Services Individually

#### Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000

#### Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:3000

## Development Workflow

### Backend Development

#### Adding a New Model

1. Create model in `backend/app/models/your_model.py`
2. Import in `backend/alembic/env.py`
3. Generate migration: `alembic revision --autogenerate -m "Add your model"`
4. Review migration in `backend/alembic/versions/`
5. Run migration: `alembic upgrade head`

#### Adding a New API Endpoint

1. Create Pydantic schemas in `backend/app/schemas/`
2. Implement business logic in `backend/app/services/`
3. Create endpoint in `backend/app/api/v1/endpoints/`
4. Register router in `backend/app/main.py`

#### Running Tests

```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_auth.py # Run specific test file
pytest -k test_login      # Run tests matching pattern
```

### Frontend Development

#### Adding a New Page

1. Create page in `frontend/src/app/your-page/page.tsx`
2. Add route in navigation if needed
3. Create components in `frontend/src/components/`

#### Adding a New API Call

1. Define types in `frontend/src/types/`
2. Add API method in `frontend/src/lib/api/`
3. Create React Query hook if needed

#### Running Tests

```bash
cd frontend
npm test              # Run all tests
npm run type-check    # TypeScript check
npm run lint          # Lint check
npm run format        # Format code
```

## Database Operations

### Creating Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Running Migrations

```bash
alembic upgrade head        # Upgrade to latest
alembic upgrade +1          # Upgrade one version
alembic downgrade -1        # Rollback one version
alembic downgrade base      # Rollback all
```

### Viewing Migration History

```bash
alembic history
alembic current
```

### Accessing Database

```bash
# Via Docker
docker exec -it edupilot-postgres psql -U edupilot -d edupilot

# Direct connection
psql -h localhost -U edupilot -d edupilot
```

## Testing Firebase Authentication

1. Set up Firebase project at https://console.firebase.google.com
2. Enable Phone Authentication
3. Download service account credentials
4. Place in `backend/firebase-credentials.json`
5. Update frontend `.env.local` with Firebase config

## AI Services Setup

### Claude API

1. Get API key from https://console.anthropic.com
2. Add to `backend/.env`: `ANTHROPIC_API_KEY=your_key`

### RAG System

The RAG system uses:
- **Chroma DB**: Vector database for NCERT content
- **HuggingFace**: Sentence transformers for embeddings
- **LangChain**: RAG orchestration

NCERT content will be ingested in Phase 4.

## Debugging

### Backend Debugging

Enable debug logs in `backend/app/core/config.py`:

```python
DEBUG = True
```

View logs:

```bash
docker-compose logs -f backend
```

### Frontend Debugging

1. Open browser DevTools (F12)
2. Check Console for errors
3. Check Network tab for API calls
4. Use React DevTools extension

### Database Debugging

Enable SQL query logging:

```python
# In backend/app/database.py
engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # Prints all SQL queries
)
```

## Code Quality

### Backend

```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

### Frontend

```bash
# Format code
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

## Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :3000  # or :8000, :5432, etc.

# Kill process
kill -9 <PID>
```

### Database Connection Error

1. Check PostgreSQL is running: `docker ps`
2. Check connection string in `.env`
3. Restart PostgreSQL: `docker-compose restart postgres`

### Module Not Found (Backend)

1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`

### Module Not Found (Frontend)

1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again

## Performance Tips

1. Use Redis caching for repeated AI queries
2. Optimize database queries with proper indexes
3. Use React Query for efficient data fetching
4. Lazy load images and components
5. Use Next.js Image component for optimization

## Next Steps

After completing Phase 1 setup, proceed to:
- **Phase 2**: Implement database models
- **Phase 3**: Build authentication system
- **Phase 4**: Set up AI services and RAG

See the main plan document for detailed implementation steps.
