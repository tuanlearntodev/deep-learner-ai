from app.graph.main_graph.state import AgentState
from app.graph.rag_graph import rag_graph
from app.graph.rag_graph.state import GraphState
from langchain_core.messages import AIMessage


def node_rag_bridge(state: AgentState) -> dict:
    print("---MAIN GRAPH: Calling RAG Sub-Graph---")
    question = state["messages"][-1].content
    workspace_id = state.get("workspace_id", "")
    
    print(f"📂 RAG Bridge - Workspace ID: {workspace_id}")
    
    sub_graph_input = GraphState(
        question=question,
        documents=[],
        answer_found=False,
        generation="",
        web_search=state["web_search"],
        crag=state["crag"],
        subject=state["subject"],
        workspace_id=workspace_id  # Pass workspace_id to RAG graph
    )
    
    final_state = rag_graph.invoke(sub_graph_input)
    
    answer = final_state["generation"]
    
    return {"messages": [AIMessage(content=answer)]}
