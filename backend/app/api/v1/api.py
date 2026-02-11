"""
API v1 router - combines all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, subjects, topics, learning

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(topics.router, prefix="/topics", tags=["Topics"])
api_router.include_router(learning.router, prefix="/learning", tags=["Learning"])

# Future routers will be added here:
# api_router.include_router(students.router, prefix="/students", tags=["Students"])
# api_router.include_router(worksheets.router, prefix="/worksheets", tags=["Worksheets"])
# api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes"])
# api_router.include_router(doubts.router, prefix="/doubts", tags=["Doubts"])
# api_router.include_router(progress.router, prefix="/progress", tags=["Progress"])
# api_router.include_router(parents.router, prefix="/parents", tags=["Parents"])
