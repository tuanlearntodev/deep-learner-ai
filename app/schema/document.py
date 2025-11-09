from datetime import datetime

from typing import Optional
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)


class DocumentCreate(DocumentBase):
    workspace_id: int = Field(..., gt=0)


class DocumentResponse(DocumentBase):
    id: int
    workspace_id: int
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    documents: list[DocumentResponse]
    total: int
    skip: int
    limit: int


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    message: str
    chunks_created: int
    file_path: str
