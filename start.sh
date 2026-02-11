#!/bin/bash

# EduPilot AI - Start Script
# Starts all services using Docker Compose

set -e

echo "🚀 Starting EduPilot AI..."

# Start all services
docker-compose up -d

echo "✅ All services started!"
echo ""
echo "Services running:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop services with: docker-compose down"
