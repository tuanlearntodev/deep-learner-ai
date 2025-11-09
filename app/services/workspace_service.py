from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.model.workspace import Workspace
from app.model.chat_message import ChatMessage
from app.model.document import Document

def get_workspace_by_id(db: Session, workspace_id: int, user_id: int) -> Optional[Workspace]:
    return db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()

def get_workspaces_by_user(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None
) -> tuple[list[Workspace], int]:
    query = db.query(Workspace).filter(Workspace.user_id == user_id)
    if search:
        query = query.filter(Workspace.name.ilike(f"%{search}%"))
    
    total = query.count()
    workspaces = query.offset(skip).limit(limit).all()
    
    return workspaces, total


def get_workspace_details(db: Session, workspace_id: int, user_id: int) -> Optional[dict]:
    workspace = get_workspace_by_id(db, workspace_id, user_id)
    if not workspace:
        return None
    message_count = db.query(func.count(ChatMessage.id)).filter(
        ChatMessage.workspace_id == workspace_id
    ).scalar() or 0
    
    document_count = db.query(func.count(Document.id)).filter(
        Document.workspace_id == workspace_id
    ).scalar() or 0
    
    return {
        "id": workspace.id,
        "name": workspace.name,
        "user_id": workspace.user_id,
        "message_count": message_count,
        "document_count": document_count
    }


def create_workspace(db: Session, name: str, user_id: int, subject: Optional[str] = None) -> Workspace:
    workspace = Workspace(
        name=name,
        subject=subject,
        user_id=user_id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace

def update_workspace(
    db: Session, 
    workspace_id: int, 
    user_id: int, 
    name: Optional[str] = None,
    subject: Optional[str] = None
) -> Optional[Workspace]:
    workspace = get_workspace_by_id(db, workspace_id, user_id)
    if not workspace:
        return None
    if name is not None:
        workspace.name = name
    
    if subject is not None:
        workspace.subject = subject
    
    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, workspace_id: int, user_id: int) -> bool:
    workspace = get_workspace_by_id(db, workspace_id, user_id)
    if not workspace:
        return False
    try:
        from app.services.redis_memory_service import clear_conversation_memory
        clear_conversation_memory(workspace_id, user_id)
    except Exception as e:
        print(f"Warning: Could not clear Redis memory for workspace {workspace_id}: {e}")
    
    db.delete(workspace)
    db.commit()
    return True


def check_workspace_exists(db: Session, workspace_id: int, user_id: int) -> bool:
    return db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).count() > 0
