from pydantic import BaseModel, EmailStr, Field

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str | None = None
    user_id: int | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    class Config:
        from_attributes = True
