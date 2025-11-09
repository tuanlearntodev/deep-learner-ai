from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schema.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessageResponse
)
from app.services.dependencies import get_db, get_current_active_user
from app.services.chat_service import (
    process_chat_message,
    get_chat_history,
    clear_chat_history
)
from app.services.workspace_service import check_workspace_exists
from app.model.user import User

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Send a message to the AI agent and get a response. Both messages are stored in the workspace."
)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    if not check_workspace_exists(db, chat_request.workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {chat_request.workspace_id} not found"
        )
    try:
        user_msg, ai_msg, response_type, questions_data = process_chat_message(
            db=db,
            workspace_id=chat_request.workspace_id,
            user_id=current_user.id,
            user_message=chat_request.message,
            web_search=chat_request.web_search,
            crag=chat_request.crag
        )
        
        from app.services.workspace_service import get_workspace_by_id
        workspace = get_workspace_by_id(db, chat_request.workspace_id, current_user.id)
        
        return ChatResponse(
            workspace_id=chat_request.workspace_id,
            user_message=ChatMessageResponse(
                id=user_msg.id,
                workspace_id=user_msg.workspace_id,
                role=user_msg.role,
                content=user_msg.content
            ),
            ai_message=ChatMessageResponse(
                id=ai_msg.id,
                workspace_id=ai_msg.workspace_id,
                role=ai_msg.role,
                content=ai_msg.content
            ),
            subject=workspace.subject if workspace else None,
            response_type=response_type,
            questions=questions_data
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get(
    "/history/{workspace_id}",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="Retrieve chat history for a specific workspace."
)
async def get_workspace_chat_history(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(50, ge=1, le=500, description="Maximum number of messages to return")
):
    if not check_workspace_exists(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    try:
        messages = get_chat_history(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id,
            limit=limit
        )
        
        return ChatHistoryResponse(
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    workspace_id=msg.workspace_id,
                    role=msg.role,
                    content=msg.content
                )
                for msg in messages
            ],
            total=len(messages),
            workspace_id=workspace_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}"
        )


@router.delete(
    "/history/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear chat history",
    description="Delete all chat messages for a workspace."
)
async def clear_workspace_chat_history(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    try:
        success = clear_chat_history(
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
            detail=f"Error clearing chat history: {str(e)}"
        )
