from app.graph.main_graph.state import AgentState
from app.graph.main_graph.chain.chat import chat_chain
from langchain_core.messages import AIMessage


def node_conversation(state: AgentState) -> dict:
    """
    Conversation node that handles general chat using message history as context.
    """
    print("---MAIN GRAPH: Conversation Node---")
    
    # Messages are already in LangChain format, use directly
    response = chat_chain.invoke({"messages": state["messages"]})
    
    # Return the AI response as AIMessage
    return {"messages": [AIMessage(content=response.content)]}
