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
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not workspace:
        raise ValueError(f"Workspace {workspace_id} not found or access denied")
    
    subject = workspace.subject or "general learning"
    
    state: AgentState = {
        "messages": [HumanMessage(content=user_message)],
        "workspace_id": str(workspace_id),
        "web_search": web_search,
        "crag": crag,
        "subject": subject
    }
    
    config = get_conversation_config(workspace_id, user_id)
    
    result = main_graph.invoke(state, config)
    
    ai_response = result["messages"][-1].content
    
    user_msg = save_message(
        db=db,
        workspace_id=workspace_id,
        role="user",
        content=user_message
    )
    
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
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    if not workspace:
        return False
    
    db.query(ChatMessage).filter(
        ChatMessage.workspace_id == workspace_id
    ).delete()
    db.commit()
    
    clear_conversation_memory(workspace_id, user_id)
    
    return True
