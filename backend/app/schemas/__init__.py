"""
Pydantic schemas for API validation
"""

from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.student import StudentBase, StudentCreate, StudentUpdate, StudentResponse
from app.schemas.parent import ParentBase, ParentCreate, ParentUpdate, ParentResponse
from app.schemas.subject import SubjectBase, SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.topic import TopicBase, TopicCreate, TopicUpdate, TopicResponse
from app.schemas.worksheet import (
    WorksheetResponse,
    WorksheetSubmissionResponse,
)
from app.schemas.quiz import (
    QuizResponse,
    QuizAttemptResponse,
)
from app.schemas.doubt import (
    MessageCreate,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ChatRequest,
    ChatResponse,
)
from app.schemas.progress import (
    ProgressRecordBase,
    ProgressRecordCreate,
    ProgressRecordUpdate,
    ProgressRecordResponse,
    WeakAreaBase,
    WeakAreaCreate,
    WeakAreaResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Student
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    # Parent
    "ParentBase",
    "ParentCreate",
    "ParentUpdate",
    "ParentResponse",
    # Subject
    "SubjectBase",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    # Topic
    "TopicBase",
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    # Worksheet
    "WorksheetResponse",
    "WorksheetSubmissionResponse",
    # Quiz
    "QuizResponse",
    "QuizAttemptResponse",
    # Conversation / Doubts
    "MessageCreate",
    "MessageResponse",
    "ConversationCreate",
    "ConversationResponse",
    "ConversationListResponse",
    "ChatRequest",
    "ChatResponse",
    # Progress
    "ProgressRecordBase",
    "ProgressRecordCreate",
    "ProgressRecordUpdate",
    "ProgressRecordResponse",
    "WeakAreaBase",
    "WeakAreaCreate",
    "WeakAreaResponse",
]
