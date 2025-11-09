"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr, Field


class UserSignup(BaseModel):
    """Schema for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: str | None = None
    user_id: int | None = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True
