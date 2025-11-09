"""
Redis memory service for managing LangGraph checkpoint state.
"""
from typing import Optional, List, Dict, Any
from langgraph.checkpoint.base import CheckpointTuple, empty_checkpoint
from app.graph.main_graph.graph import main_graph


def get_thread_id(workspace_id: int, user_id: int) -> str:
    """
    Generate a consistent thread_id for a workspace conversation.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        Thread ID string
    """
    return f"workspace_{workspace_id}_user_{user_id}"


def get_conversation_config(workspace_id: int, user_id: int) -> dict:
    """
    Get the configuration dictionary for graph invocation with checkpointer.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        Configuration dictionary with thread_id
    """
    return {
        "configurable": {
            "thread_id": get_thread_id(workspace_id, user_id)
        }
    }


def clear_conversation_memory(workspace_id: int, user_id: int) -> bool:
    """
    Clear the Redis checkpoint memory for a specific workspace conversation.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        config = get_conversation_config(workspace_id, user_id)
        checkpointer = main_graph.checkpointer
        
        if checkpointer:
            # Put an empty checkpoint to clear the thread history
            checkpointer.put(config, empty_checkpoint(), {}, {})
            return True
        return False
    except Exception as e:
        print(f"Error clearing conversation memory: {e}")
        return False


def get_conversation_state(workspace_id: int, user_id: int) -> Optional[CheckpointTuple]:
    """
    Get the current checkpoint state for a workspace conversation.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        CheckpointTuple if exists, None otherwise
    """
    try:
        config = get_conversation_config(workspace_id, user_id)
        checkpointer = main_graph.checkpointer
        
        if checkpointer:
            return checkpointer.get_tuple(config)
        return None
    except Exception as e:
        print(f"Error getting conversation state: {e}")
        return None


def list_conversation_checkpoints(workspace_id: int, user_id: int) -> List[CheckpointTuple]:
    """
    List all checkpoints for a workspace conversation.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        List of CheckpointTuple objects
    """
    try:
        config = get_conversation_config(workspace_id, user_id)
        checkpointer = main_graph.checkpointer
        
        if checkpointer:
            return list(checkpointer.list(config))
        return []
    except Exception as e:
        print(f"Error listing conversation checkpoints: {e}")
        return []


def get_conversation_metadata(workspace_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get metadata about the conversation state in Redis.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID
    
    Returns:
        Dictionary with metadata or None
    """
    try:
        checkpoint_tuple = get_conversation_state(workspace_id, user_id)
        if checkpoint_tuple and checkpoint_tuple.checkpoint:
            return {
                "thread_id": get_thread_id(workspace_id, user_id),
                "has_checkpoint": True,
                "checkpoint_id": checkpoint_tuple.checkpoint.get("id"),
                "metadata": checkpoint_tuple.metadata
            }
        return {
            "thread_id": get_thread_id(workspace_id, user_id),
            "has_checkpoint": False
        }
    except Exception as e:
        print(f"Error getting conversation metadata: {e}")
        return None
