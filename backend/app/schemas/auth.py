"""
Authentication Pydantic schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.models.user import UserType
from app.schemas.user import UserResponse
from app.schemas.student import StudentResponse
from app.schemas.parent import ParentResponse


class PhoneLoginRequest(BaseModel):
    """Request schema for phone login initiation"""
    phone_number: str = Field(..., min_length=10, max_length=15)

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        # Remove spaces and dashes
        phone = v.replace(" ", "").replace("-", "")

        # Should start with + or country code
        if not phone.startswith("+"):
            # Assume Indian number if no country code
            if phone.startswith("91"):
                phone = "+" + phone
            else:
                phone = "+91" + phone

        return phone


class VerifyOTPRequest(BaseModel):
    """Request schema for OTP verification"""
    id_token: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    id_token: str = Field(..., min_length=1)
    user_type: UserType
    name: str = Field(..., min_length=1, max_length=100)
    grade: Optional[int] = Field(None, ge=3, le=10)  # Required for students
    email: Optional[str] = None

    @field_validator('grade')
    @classmethod
    def validate_grade_for_student(cls, v: Optional[int], info) -> Optional[int]:
        """Validate that students have a grade"""
        user_type = info.data.get('user_type')
        if user_type == UserType.STUDENT and v is None:
            raise ValueError('Grade is required for students')
        return v


class LoginResponse(BaseModel):
    """Response schema for successful login/registration"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    student: Optional[StudentResponse] = None
    parent: Optional[ParentResponse] = None


class TokenResponse(BaseModel):
    """Simple token response"""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
