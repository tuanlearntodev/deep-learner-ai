"""
Pydantic schemas for workspace management.
"""
from pydantic import BaseModel, Field
from typing import Optional


class WorkspaceBase(BaseModel):
    """Base schema for workspace."""
    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace subject")


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a workspace."""
    pass


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace name")
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace subject")


class WorkspaceResponse(WorkspaceBase):
    """Schema for workspace response."""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


class WorkspaceDetails(WorkspaceResponse):
    """Schema for workspace with statistics."""
    message_count: int = Field(default=0, description="Total messages in workspace")
    document_count: int = Field(default=0, description="Total documents in workspace")
    
    class Config:
        from_attributes = True


class WorkspaceList(BaseModel):
    """Schema for paginated workspace list."""
    workspaces: list[WorkspaceResponse]
    total: int
    skip: int
    limit: int
