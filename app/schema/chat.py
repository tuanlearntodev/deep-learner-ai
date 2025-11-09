"""
Pydantic schemas for chat operations.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessageBase(BaseModel):
    """Base schema for chat messages."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message content")


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    content: str = Field(..., min_length=1, description="User message content")


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response."""
    id: int
    workspace_id: int
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""
    workspace_id: int = Field(..., description="Workspace ID for the chat")
    message: str = Field(..., min_length=1, description="User message")
    web_search: Optional[bool] = Field(default=False, description="Enable web search")
    crag: Optional[bool] = Field(default=False, description="Enable corrective RAG")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    workspace_id: int
    user_message: ChatMessageResponse
    ai_message: ChatMessageResponse
    subject: Optional[str] = Field(None, description="Workspace subject")


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""
    messages: List[ChatMessageResponse]
    total: int
    workspace_id: int
