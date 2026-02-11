# EduPilot AI - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### Step 1: Navigate to Project

```bash
cd /Users/prasadreddy/projects/edupilot-ai
```

### Step 2: Run Setup (First Time Only)

```bash
./setup.sh
```

This will:
- ✅ Check prerequisites (Python, Node.js, Docker)
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies
- ✅ Install all frontend dependencies
- ✅ Start PostgreSQL and Redis
- ✅ Run database migrations
- ✅ Create .env files

### Step 3: Configure Environment Variables

#### Backend (.env)

```bash
cd backend
nano .env  # or use your favorite editor
```

Required variables:
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
SECRET_KEY=your_secret_key_here
```

#### Frontend (.env.local)

```bash
cd frontend
nano .env.local
```

Required variables:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
# ... other Firebase config
```

### Step 4: Start Services

```bash
./start.sh
```

Or start manually:

```bash
# Start databases
docker-compose up -d postgres redis

# Start backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Start frontend (Terminal 2)
cd frontend
npm run dev
```

### Step 5: Access Application

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🗄️ **PostgreSQL**: localhost:5432
- 💾 **Redis**: localhost:6379

---

## 🧪 Verify Everything Works

### Test Backend

```bash
curl http://localhost:8000/
# Expected: {"message": "EduPilot AI API", "status": "running"}
```

### Test Frontend

Open http://localhost:3000 in your browser
- Should see landing page
- Should see "EduPilot AI" header

### Test Database

```bash
docker exec -it edupilot-postgres psql -U edupilot -c "SELECT version();"
# Should show PostgreSQL version
```

### Test Redis

```bash
docker exec -it edupilot-redis redis-cli ping
# Should return: PONG
```

---

## 📁 Project Structure at a Glance

```
edupilot-ai/
├── backend/        # FastAPI + Python
│   ├── app/        # Application code
│   └── alembic/    # Database migrations
├── frontend/       # Next.js + TypeScript
│   └── src/        # Source code
├── docs/           # Documentation
└── docker-compose.yml
```

---

## 🔧 Common Commands

### Development

```bash
# Start all services
./start.sh

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend
docker-compose restart frontend
```

### Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/

# Lint
flake8 app/

# Create migration
alembic revision --autogenerate -m "Description"

# Run migration
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Type check
npm run type-check

# Lint
npm run lint

# Format
npm run format
```

### Database

```bash
# Access PostgreSQL
docker exec -it edupilot-postgres psql -U edupilot

# Backup database
docker exec edupilot-postgres pg_dump -U edupilot edupilot > backup.sql

# Restore database
cat backup.sql | docker exec -i edupilot-postgres psql -U edupilot edupilot
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process
lsof -i :3000  # or :8000, :5432, :6379
kill -9 <PID>
```

### Database Connection Failed

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check if running
docker ps | grep postgres
```

### Frontend Won't Start

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Backend Won't Start

```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 Documentation

- **Full Setup**: [README.md](README.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Development Guide**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **Phase Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🎯 What Works Now (Phase 1)

✅ Development environment
✅ Backend API (health check)
✅ Frontend landing page
✅ PostgreSQL database
✅ Redis cache
✅ Docker setup
✅ CI/CD pipeline

---

## 🚀 What's Coming Next (Phase 2)

🔜 Database models (User, Student, Parent, etc.)
🔜 Database migrations
🔜 Pydantic schemas
🔜 Database seeding

---

## 💡 Tips

1. Always activate Python venv: `source backend/venv/bin/activate`
2. Use Docker for databases: easier than local install
3. Check logs: `docker-compose logs -f <service>`
4. Hot reload works for both frontend and backend
5. API docs auto-generated: http://localhost:8000/docs

---

## 🆘 Need Help?

1. Check [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed guides
2. Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
3. See [CONTRIBUTING.md](CONTRIBUTING.md) for code guidelines
4. Check logs: `docker-compose logs -f`

---

**Ready to build! 🎉**
