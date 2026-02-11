"""
Pydantic schemas for API validation
"""

from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.student import StudentBase, StudentCreate, StudentUpdate, StudentResponse
from app.schemas.parent import ParentBase, ParentCreate, ParentUpdate, ParentResponse
from app.schemas.subject import SubjectBase, SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.topic import TopicBase, TopicCreate, TopicUpdate, TopicResponse
from app.schemas.worksheet import (
    QuestionSchema,
    WorksheetBase,
    WorksheetCreate,
    WorksheetResponse,
    WorksheetSubmissionCreate,
    WorksheetSubmissionResponse,
)
from app.schemas.quiz import (
    QuizBase,
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizAttemptCreate,
    QuizAttemptSubmit,
    QuizAttemptResponse,
)
from app.schemas.conversation import (
    MessageBase,
    MessageCreate,
    MessageResponse,
    ConversationBase,
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
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
    "QuestionSchema",
    "WorksheetBase",
    "WorksheetCreate",
    "WorksheetResponse",
    "WorksheetSubmissionCreate",
    "WorksheetSubmissionResponse",
    # Quiz
    "QuizBase",
    "QuizCreate",
    "QuizUpdate",
    "QuizResponse",
    "QuizAttemptCreate",
    "QuizAttemptSubmit",
    "QuizAttemptResponse",
    # Conversation
    "MessageBase",
    "MessageCreate",
    "MessageResponse",
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationResponse",
    "ConversationWithMessages",
    # Progress
    "ProgressRecordBase",
    "ProgressRecordCreate",
    "ProgressRecordUpdate",
    "ProgressRecordResponse",
    "WeakAreaBase",
    "WeakAreaCreate",
    "WeakAreaResponse",
]
