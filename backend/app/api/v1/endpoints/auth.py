"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.core.config import settings
from app.services.firebase_service import firebase_service
from app.models import User, Student, Parent
from app.models.user import UserType
from app.schemas.auth import (
    RegisterRequest,
    VerifyOTPRequest,
    LoginResponse,
    MessageResponse
)
from app.schemas.user import UserResponse
from app.schemas.student import StudentResponse
from app.schemas.parent import ParentResponse
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (student or parent) with Firebase ID token

    - Verifies Firebase ID token
    - Creates user account
    - Creates student or parent profile
    - Returns JWT access token
    """
    try:
        # Verify Firebase ID token
        decoded_token = firebase_service.verify_id_token(request.id_token)
        phone_number = decoded_token.get('phone_number')

        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number not found in token"
            )

        # Check if user already exists
        existing_user = db.query(User).filter(User.phone_number == phone_number).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists"
            )

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            user_type=request.user_type,
            is_active="1"
        )
        db.add(user)
        db.flush()

        # Create student or parent profile
        student = None
        parent = None

        if request.user_type == UserType.STUDENT:
            if request.grade is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Grade is required for students"
                )

            student = Student(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=request.name,
                grade=request.grade,
                email=request.email
            )
            db.add(student)

        elif request.user_type == UserType.PARENT:
            parent = Parent(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=request.name,
                email=request.email
            )
            db.add(parent)

        db.commit()
        db.refresh(user)

        # Generate JWT access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "type": user.user_type.value},
            expires_delta=access_token_expires
        )

        # Prepare response
        user_response = UserResponse.model_validate(user)
        student_response = StudentResponse.model_validate(student) if student else None
        parent_response = ParentResponse.model_validate(parent) if parent else None

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
            student=student_response,
            parent=parent_response
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=LoginResponse)
def login_user(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Login existing user with Firebase ID token

    - Verifies Firebase ID token
    - Checks if user exists
    - Returns JWT access token with user info
    """
    try:
        # Verify Firebase ID token
        decoded_token = firebase_service.verify_id_token(request.id_token)
        phone_number = decoded_token.get('phone_number')

        if not phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number not found in token"
            )

        # Find user by phone number
        user = db.query(User).filter(User.phone_number == phone_number).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register first."
            )

        if user.is_active != "1":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Get student or parent profile
        student = None
        parent = None

        if user.user_type == UserType.STUDENT:
            student = db.query(Student).filter(Student.user_id == user.id).first()
        elif user.user_type == UserType.PARENT:
            parent = db.query(Parent).filter(Parent.user_id == user.id).first()

        # Generate JWT access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "type": user.user_type.value},
            expires_delta=access_token_expires
        )

        # Prepare response
        user_response = UserResponse.model_validate(user)
        student_response = StudentResponse.model_validate(student) if student else None
        parent_response = ParentResponse.model_validate(parent) if parent else None

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
            student=student_response,
            parent=parent_response
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.get("/me", response_model=LoginResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information

    - Returns user profile
    - Returns student or parent profile
    - Requires valid JWT token
    """
    try:
        # Get student or parent profile
        student = None
        parent = None

        if current_user.user_type == UserType.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
        elif current_user.user_type == UserType.PARENT:
            parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()

        # Prepare response (no new token needed)
        user_response = UserResponse.model_validate(current_user)
        student_response = StudentResponse.model_validate(student) if student else None
        parent_response = ParentResponse.model_validate(parent) if parent else None

        # Return current token (client already has it)
        return LoginResponse(
            access_token="",  # Client already has valid token
            token_type="bearer",
            user=user_response,
            student=student_response,
            parent=parent_response
        )

    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.post("/dev-login", response_model=LoginResponse)
def dev_login(
    db: Session = Depends(get_db)
):
    """
    Development-only login that bypasses Firebase.
    Creates or retrieves a test student account.
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev login is only available in development mode"
        )

    phone_number = "+919999999999"

    # Find or create test user
    user = db.query(User).filter(User.phone_number == phone_number).first()

    if not user:
        user = User(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            user_type=UserType.STUDENT,
            is_active="1"
        )
        db.add(user)
        db.flush()

        student = Student(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name="Test Student",
            grade=8,
        )
        db.add(student)
        db.commit()
        db.refresh(user)

    student = db.query(Student).filter(Student.user_id == user.id).first()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "type": user.user_type.value},
        expires_delta=access_token_expires
    )

    user_response = UserResponse.model_validate(user)
    student_response = StudentResponse.model_validate(student) if student else None

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response,
        student=student_response,
        parent=None
    )


@router.post("/logout", response_model=MessageResponse)
def logout_user(current_user: User = Depends(get_current_user)):
    """
    Logout user (client-side token removal)

    - In stateless JWT, logout is handled client-side
    - This endpoint confirms logout action
    """
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh JWT access token

    - Issues new access token
    - Returns updated user information
    """
    try:
        # Get student or parent profile
        student = None
        parent = None

        if current_user.user_type == UserType.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
        elif current_user.user_type == UserType.PARENT:
            parent = db.query(Parent).filter(Parent.user_id == current_user.id).first()

        # Generate new JWT access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.id, "type": current_user.user_type.value},
            expires_delta=access_token_expires
        )

        # Prepare response
        user_response = UserResponse.model_validate(current_user)
        student_response = StudentResponse.model_validate(student) if student else None
        parent_response = ParentResponse.model_validate(parent) if parent else None

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
            student=student_response,
            parent=parent_response
        )

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )
