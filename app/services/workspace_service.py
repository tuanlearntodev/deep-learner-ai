"""
Service layer for workspace operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.model.workspace import Workspace
from app.model.chat_message import ChatMessage
from app.model.document import Document


def get_workspace_by_id(db: Session, workspace_id: int, user_id: int) -> Optional[Workspace]:
    """
    Get workspace by ID for a specific user.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID who owns the workspace
    
    Returns:
        Workspace object or None if not found
    """
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
    """
    Get all workspaces for a user with pagination and optional search.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term for workspace name
    
    Returns:
        Tuple of (list of workspaces, total count)
    """
    query = db.query(Workspace).filter(Workspace.user_id == user_id)
    
    if search:
        query = query.filter(Workspace.name.ilike(f"%{search}%"))
    
    total = query.count()
    workspaces = query.offset(skip).limit(limit).all()
    
    return workspaces, total


def get_workspace_details(db: Session, workspace_id: int, user_id: int) -> Optional[dict]:
    """
    Get workspace with message and document counts.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        Dictionary with workspace details and counts or None
    """
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
    """
    Create a new workspace for a user.
    
    Args:
        db: Database session
        name: Workspace name
        user_id: User ID
    
    Returns:
        Created workspace object
    """
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
    """
    Update workspace properties.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID
        name: Optional new workspace name
        subject: Optional workspace subject
    
    Returns:
        Updated workspace object or None if not found
    """
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
    """
    Delete a workspace and all associated data (cascade).
    Also clears Redis checkpoint memory for the workspace.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        True if deleted, False if not found
    """
    workspace = get_workspace_by_id(db, workspace_id, user_id)
    if not workspace:
        return False
    
    # Clear Redis checkpoint memory before deleting
    try:
        from app.services.redis_memory_service import clear_conversation_memory
        clear_conversation_memory(workspace_id, user_id)
    except Exception as e:
        print(f"Warning: Could not clear Redis memory for workspace {workspace_id}: {e}")
    
    db.delete(workspace)
    db.commit()
    return True


def check_workspace_exists(db: Session, workspace_id: int, user_id: int) -> bool:
    """
    Check if a workspace exists and belongs to the user.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        True if exists, False otherwise
    """
    return db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).count() > 0
