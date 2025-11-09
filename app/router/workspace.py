from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schema.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceDetails,
    WorkspaceList
)
from app.services.dependencies import get_db, get_current_active_user
from app.services.workspace_service import (
    get_workspace_by_id,
    get_workspaces_by_user,
    get_workspace_details,
    create_workspace,
    update_workspace,
    delete_workspace,
    check_workspace_exists
)
from app.services.redis_memory_service import get_conversation_metadata, clear_conversation_memory
from app.model.user import User

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "/",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workspace",
    description="Create a new workspace for the authenticated user."
)
async def create_new_workspace(
    workspace_data: WorkspaceCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    try:
        workspace = create_workspace(
            db=db,
            name=workspace_data.name,
            user_id=current_user.id,
            subject=workspace_data.subject
        )
        return workspace
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this name already exists"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid request data. This endpoint expects JSON with 'name' and optional 'subject' fields. For file uploads, use POST /workspaces/{{workspace_id}}/documents/upload"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating workspace: {str(e)}"
        )

@router.get(
    "/",
    response_model=WorkspaceList,
    summary="List all workspaces",
    description="Get a paginated list of all workspaces for the authenticated user."
)
async def list_user_workspaces(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for workspace name")
):
    workspaces, total = get_workspaces_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search
    )
    return {
        "workspaces": workspaces,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get workspace by ID",
    description="Get a specific workspace by its ID."
)
async def get_workspace(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    workspace = get_workspace_by_id(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    
    return workspace


@router.get(
    "/{workspace_id}/details",
    response_model=WorkspaceDetails,
    summary="Get workspace details with statistics",
    description="Get workspace with message and document counts."
)
async def get_workspace_with_stats(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    workspace = get_workspace_details(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id
    )
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    
    return workspace


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace",
    description="Update workspace properties (currently only name)."
)
async def update_workspace_endpoint(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    if not check_workspace_exists(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    try:
        workspace = update_workspace(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id,
            name=workspace_data.name,
            subject=workspace_data.subject
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace with ID {workspace_id} not found"
            )
        
        return workspace
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this name already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating workspace: {str(e)}"
        )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
    description="Delete a workspace and all associated data (messages, documents)."
)
async def delete_workspace_endpoint(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    try:
        success = delete_workspace(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace with ID {workspace_id} not found"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting workspace: {str(e)}"
        )


@router.get(
    "/{workspace_id}/exists",
    summary="Check if workspace exists",
    description="Check if a workspace exists and belongs to the user."
)
async def check_workspace(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    exists = check_workspace_exists(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id
    )
    return {
        "exists": exists,
        "workspace_id": workspace_id
    }


@router.get(
    "/{workspace_id}/memory",
    summary="Get Redis memory status",
    description="Get information about the Redis checkpoint memory for this workspace."
)
async def get_workspace_memory_status(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    if not check_workspace_exists(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    try:
        metadata = get_conversation_metadata(workspace_id, current_user.id)
        return metadata or {"error": "Could not retrieve memory metadata"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving memory status: {str(e)}"
        )


@router.delete(
    "/{workspace_id}/memory",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear Redis memory",
    description="Clear the Redis checkpoint memory for this workspace without deleting chat history."
)
async def clear_workspace_memory(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    if not check_workspace_exists(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    try:
        success = clear_conversation_memory(workspace_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear memory"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing memory: {str(e)}"
        )
