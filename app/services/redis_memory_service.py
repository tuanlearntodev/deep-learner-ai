from typing import Optional, List, Dict, Any
from langgraph.checkpoint.base import CheckpointTuple, empty_checkpoint
from app.graph.main_graph.graph import checkpointer

def get_thread_id(workspace_id: int, user_id: int) -> str:
    """Generate a unique thread ID for a workspace and user combination."""
    return f"workspace_{workspace_id}_user_{user_id}"

def get_conversation_config(workspace_id: int, user_id: int) -> dict:
    """
    Get the configuration for conversation state management.
    This config is used by LangGraph to identify and persist conversation state.
    """
    return {
        "configurable": {
            "thread_id": get_thread_id(workspace_id, user_id)
        }
    }

def clear_conversation_memory(workspace_id: int, user_id: int) -> bool:
    """
    Clear all conversation memory for a specific workspace and user.
    This removes all checkpoints from Redis for the given thread.
    """
    try:
        config = get_conversation_config(workspace_id, user_id)
        if checkpointer:
            # Put an empty checkpoint to clear the conversation history
            checkpointer.put(config, empty_checkpoint(), {}, {})
            return True
        return False
    except Exception as e:
        print(f"❌ Error clearing conversation memory: {e}")
        return False


def get_conversation_state(workspace_id: int, user_id: int) -> Optional[CheckpointTuple]:
    """
    Retrieve the current conversation state from Redis.
    Returns the latest checkpoint for the conversation thread.
    """
    try:
        config = get_conversation_config(workspace_id, user_id)
        if checkpointer:
            return checkpointer.get_tuple(config)
        return None
    except Exception as e:
        print(f"❌ Error getting conversation state: {e}")
        return None


def list_conversation_checkpoints(workspace_id: int, user_id: int) -> List[CheckpointTuple]:
    """
    List all checkpoints for a conversation thread.
    Useful for debugging and viewing conversation history.
    """
    try:
        config = get_conversation_config(workspace_id, user_id)
        if checkpointer:
            return list(checkpointer.list(config))
        return []
    except Exception as e:
        print(f"❌ Error listing conversation checkpoints: {e}")
        return []


def get_conversation_metadata(workspace_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get metadata about the conversation state including thread ID and checkpoint info.
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
        print(f"❌ Error getting conversation metadata: {e}")
        return None
