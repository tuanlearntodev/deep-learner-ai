from app.graph.main_graph.state import AgentState
from app.graph.main_graph.chain.chat import chat_chain
from langchain_core.messages import AIMessage


def node_conversation(state: AgentState) -> dict:
    print("---MAIN GRAPH: Conversation Node---")
    subject = state.get("subject", "general learning")
    
    response = chat_chain.invoke({"messages": state["messages"], "subject": subject})
    
    return {"messages": [AIMessage(content=response.content)]}
