#!/bin/bash

# EduPilot AI - Setup Script
# This script sets up the development environment for EduPilot AI

set -e

echo "🚀 Setting up EduPilot AI..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.11+${NC}"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites found${NC}"

# Setup Backend
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update backend/.env with your API keys${NC}"
fi

cd ..

# Setup Frontend
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Copy .env.example to .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from .env.example..."
    cp .env.example .env.local
    echo -e "${YELLOW}⚠️  Please update frontend/.env.local with your Firebase config${NC}"
fi

cd ..

# Start Docker services
echo -e "\n${YELLOW}Starting Docker services...${NC}"
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec edupilot-postgres pg_isready -U edupilot; do
    sleep 1
done

echo -e "${GREEN}✓ PostgreSQL is ready${NC}"

# Run database migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
cd backend
source venv/bin/activate
alembic upgrade head
cd ..

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\nNext steps:"
echo -e "  1. Update ${YELLOW}backend/.env${NC} with your API keys (Claude, Firebase)"
echo -e "  2. Update ${YELLOW}frontend/.env.local${NC} with your Firebase config"
echo -e "  3. Run ${YELLOW}./start.sh${NC} to start the application"
echo -e "\nOr run services individually:"
echo -e "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo -e "  Frontend: cd frontend && npm run dev"
