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
    limit: Optional[int] = 150
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
    
    # Load previous chat history from database
    previous_messages = get_chat_history(db, workspace_id, user_id, limit=150)
    
    # Convert to LangChain messages and add current message
    langchain_messages = convert_to_langchain_messages(previous_messages)
    langchain_messages.append(HumanMessage(content=user_message))
    
    print(f"💬 Loaded {len(previous_messages)} previous messages from database")
    
    state: AgentState = {
        "messages": langchain_messages,
        "workspace_id": str(workspace_id),
        "web_search": web_search,
        "crag": crag,
        "subject": subject
    }
    
    config = get_conversation_config(workspace_id, user_id)
    
    result = main_graph.invoke(state, config)
    
    ai_message = result["messages"][-1]
    ai_response = ai_message.content
    
    # Extract response type from message metadata
    response_type = ai_message.additional_kwargs.get("response_type", "text") if hasattr(ai_message, "additional_kwargs") else "text"
    
    # Parse JSON questions/evaluation if applicable
    import json
    questions_data = None
    
    # For evaluation responses, keep the JSON content as-is for frontend
    if response_type == "evaluation":
        # Evaluation data is already in JSON format in the content
        # Frontend will parse it, so we don't need questions_data
        pass
    elif response_type in ["questions", "quiz", "flashcard"]:
        try:
            questions_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, treat as text
            response_type = "text"
    
    print(f"💾 Saving user message to database...")
    user_msg = save_message(
        db=db,
        workspace_id=workspace_id,
        role="user",
        content=user_message
    )
    print(f"✅ User message saved with ID: {user_msg.id}")
    
    print(f"💾 Saving AI message to database (type: {response_type})...")
    ai_msg = save_message(
        db=db,
        workspace_id=workspace_id,
        role="assistant",
        content=ai_response
    )
    print(f"✅ AI message saved with ID: {ai_msg.id}")
    
    return user_msg, ai_msg, response_type, questions_data


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
