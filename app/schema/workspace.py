from pydantic import BaseModel, Field
from typing import Optional

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace subject")

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace name")
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Workspace subject")

class WorkspaceResponse(WorkspaceBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True


class WorkspaceDetails(WorkspaceResponse):
    message_count: int = Field(default=0, description="Total messages in workspace")
    document_count: int = Field(default=0, description="Total documents in workspace")
    class Config:
        from_attributes = True


class WorkspaceList(BaseModel):
    workspaces: list[WorkspaceResponse]
    total: int
    skip: int
    limit: int
