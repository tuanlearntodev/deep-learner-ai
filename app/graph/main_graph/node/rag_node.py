from app.graph.main_graph.state import AgentState
from app.graph.rag_graph import rag_graph
from app.graph.rag_graph.state import GraphState
from langchain_core.messages import AIMessage


def node_rag_bridge(state: AgentState) -> dict:
    """
    This node in the main graph calls the RAG sub-graph.
    """
    print("---MAIN GRAPH: Calling RAG Sub-Graph---")
    
    # 1. Get the user's question from the last message
    question = state["messages"][-1].content
    
    # 2. Prepare the input for the sub-graph
    sub_graph_input = GraphState(
        question=question,
        # Set defaults for the sub-graph's state
        documents=[],
        answer_found=False,
        generation="",
        web_search=state["web_search"],
        crag=state["crag"],
        subject=state["subject"]
    )
    
    # 3. Invoke the sub-graph
    final_state = rag_graph.invoke(sub_graph_input)
    
    # 4. Get the final answer
    answer = final_state["generation"]
    
    # 5. Return the answer as AIMessage
    return {"messages": [AIMessage(content=answer)]}