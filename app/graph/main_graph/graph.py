from langgraph.graph import StateGraph, END
from app.graph.main_graph.state import AgentState
from app.graph.main_graph.node import node_rag_bridge, node_conversation
from app.graph.main_graph.chain.route import routing_chain, Router

# Initialize RedisSaver with URL directly
# saver = RedisSaver(redis_url=settings.REDIS_URL)

def router(state: AgentState) -> str:
    """
    Route to the appropriate node based on the user's query.
    """
    print("---MAIN GRAPH: Routing---")
    question = state["messages"][-1].content
    route: Router = routing_chain.invoke({"question": question})
    print(f"Router Decision: {route.node}")
    return route.node
    

# --- Build the Main Graph ---
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("rag_node", node_rag_bridge)
builder.add_node("chat_node", node_conversation)

# Set conditional entry point - routes directly to the appropriate node
builder.set_conditional_entry_point(
    router,
    {
        "rag_node": "rag_node",
        "chat_node": "chat_node"
    }
)

# Both nodes go directly to END
builder.add_edge("rag_node", END)
builder.add_edge("chat_node", END)


main_graph = builder.compile()
main_graph.get_graph.draw_mermaid_png(output_file_path="graph_workflow.png")