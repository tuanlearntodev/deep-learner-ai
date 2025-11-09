from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessageBase(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message content")

class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="User message content")

class ChatMessageResponse(ChatMessageBase):
    id: int
    workspace_id: int
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    workspace_id: int = Field(..., description="Workspace ID for the chat")
    message: str = Field(..., min_length=1, description="User message")
    web_search: Optional[bool] = Field(default=False, description="Enable web search")
    crag: Optional[bool] = Field(default=False, description="Enable corrective RAG")

class ChatResponse(BaseModel):
    workspace_id: int
    user_message: ChatMessageResponse
    ai_message: ChatMessageResponse
    subject: Optional[str] = Field(None, description="Workspace subject")
    response_type: Optional[str] = Field(default="text", description="Response type: 'text', 'questions', or 'quiz'")
    questions: Optional[List[dict]] = Field(None, description="Parsed JSON questions if response_type is 'questions' or 'quiz'")

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total: int
    workspace_id: int
