"""
Service layer for chat operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from langchain_core.messages import HumanMessage, AIMessage

from app.model.chat_message import ChatMessage
from app.model.workspace import Workspace
from app.graph.main_graph.graph import main_graph
from app.graph.main_graph.state import AgentState
from app.services.redis_memory_service import get_conversation_config, clear_conversation_memory


def get_chat_history(
    db: Session, 
    workspace_id: int, 
    user_id: int,
    limit: Optional[int] = 50
) -> List[ChatMessage]:
    """
    Get chat history for a workspace.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID who owns the workspace
        limit: Maximum number of messages to return
    
    Returns:
        List of chat messages ordered by ID (oldest first)
    """
    # First verify the workspace belongs to the user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    
    if not workspace:
        return []
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.workspace_id == workspace_id
    ).order_by(ChatMessage.id.asc())
    
    if limit:
        messages = messages.limit(limit)
    
    return messages.all()


def save_message(
    db: Session,
    workspace_id: int,
    role: str,
    content: str
) -> ChatMessage:
    """
    Save a chat message to the database.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        role: Message role ('user' or 'assistant')
        content: Message content
    
    Returns:
        Created chat message object
    """
    message = ChatMessage(
        workspace_id=workspace_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def convert_to_langchain_messages(messages: List[ChatMessage]):
    """
    Convert database chat messages to LangChain message format.
    
    Args:
        messages: List of ChatMessage objects from database
    
    Returns:
        List of LangChain message objects (HumanMessage or AIMessage)
    """
    langchain_messages = []
    for msg in messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
    return langchain_messages


def process_chat_message(
    db: Session,
    workspace_id: int,
    user_id: int,
    user_message: str,
    web_search: bool = False,
    crag: bool = False
) -> tuple[ChatMessage, ChatMessage]:
    """
    Process a chat message through the LangGraph agent and store both messages.
    Uses Redis checkpointer for conversation memory persistence.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID
        user_message: User's message content
        web_search: Enable web search
        crag: Enable corrective RAG
    
    Returns:
        Tuple of (user_message, ai_message) ChatMessage objects
    
    Raises:
        ValueError: If workspace not found or doesn't belong to user
    """
    # Verify workspace exists and belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    
    if not workspace:
        raise ValueError(f"Workspace {workspace_id} not found or access denied")
    
    # Get workspace subject
    subject = workspace.subject or "general learning"
    
    # Create the state for the agent with just the new message
    # The checkpointer will handle loading previous conversation state from Redis
    state: AgentState = {
        "messages": [HumanMessage(content=user_message)],
        "workspace_id": str(workspace_id),
        "web_search": web_search,
        "crag": crag,
        "subject": subject
    }
    
    # Get configuration with thread_id for Redis checkpointer
    config = get_conversation_config(workspace_id, user_id)
    
    # Invoke the main graph with checkpointer support
    # The graph will automatically load conversation history from Redis
    result = main_graph.invoke(state, config)
    
    # Get the AI response (last message in the result)
    ai_response = result["messages"][-1].content
    
    # Save user message
    user_msg = save_message(
        db=db,
        workspace_id=workspace_id,
        role="user",
        content=user_message
    )
    
    # Save AI message
    ai_msg = save_message(
        db=db,
        workspace_id=workspace_id,
        role="assistant",
        content=ai_response
    )
    
    return user_msg, ai_msg


def clear_chat_history(
    db: Session,
    workspace_id: int,
    user_id: int
) -> bool:
    """
    Clear all chat messages for a workspace and Redis checkpoint memory.
    
    Args:
        db: Database session
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        True if successful, False if workspace not found
    """
    # Verify workspace exists and belongs to user
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    
    if not workspace:
        return False
    
    # Delete all messages for this workspace from database
    db.query(ChatMessage).filter(
        ChatMessage.workspace_id == workspace_id
    ).delete()
    db.commit()
    
    # Clear Redis checkpoint memory for this workspace
    clear_conversation_memory(workspace_id, user_id)
    
    return True
