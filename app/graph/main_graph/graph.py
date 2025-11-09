from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver
from app.graph.main_graph.state import AgentState
from app.graph.main_graph.node import node_rag_bridge, node_conversation, node_question_generation_bridge, node_evaluation_bridge
from app.graph.main_graph.chain.route import routing_chain, Router
from app.settings import settings

# Initialize RedisSaver with URL directly
checkpointer_manager = RedisSaver.from_conn_string(settings.REDIS_URL)
checkpointer = checkpointer_manager.__enter__()

def router(state: AgentState) -> str:
    """
    Route to the appropriate node based on the user's query.
    """
    print("---MAIN GRAPH: Routing---")
    question = state["messages"][-1].content
    subject = state.get("subject", "general learning")
    route: Router = routing_chain.invoke({"question": question, "subject": subject})
    print(f"Router Decision: {route.node}")
    print(f"Subject Context: {subject}")
    return route.node
    

# --- Build the Main Graph ---
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("rag_node", node_rag_bridge)
builder.add_node("chat_node", node_conversation)
builder.add_node("question_generation_node", node_question_generation_bridge)
builder.add_node("evaluation_node", node_evaluation_bridge)

# Set conditional entry point - routes directly to the appropriate node
builder.set_conditional_entry_point(
    router,
    {
        "rag_node": "rag_node",
        "chat_node": "chat_node",
        "question_generation_node": "question_generation_node",
        "evaluation_node": "evaluation_node"
    }
)

# All nodes go directly to END
builder.add_edge("rag_node", END)
builder.add_edge("chat_node", END)
builder.add_edge("question_generation_node", END)
builder.add_edge("evaluation_node", END)


main_graph = builder.compile(checkpointer=checkpointer)