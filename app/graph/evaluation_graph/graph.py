from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from app.graph.evaluation_graph.node import evaluate_answer, generate_feedback, get_rag_answer
from app.graph.evaluation_graph.state import GraphState

load_dotenv()

RAG_ANSWER = "rag_answer"
EVALUATE = "evaluate"
FEEDBACK = "feedback"


def decide_feedback(state: GraphState) -> str:
    """Decide if detailed feedback is needed based on score."""
    print("---DECIDE FEEDBACK---")
    score = state.get("score", 0.0)
    
    # Always provide feedback for learning purposes
    # But could conditionally skip for perfect scores if desired
    if score >= 1.0:
        print("✓ Perfect score - providing acknowledgment")
        return FEEDBACK
    elif score >= 0.7:
        print("✓ Good score - providing encouragement")
        return FEEDBACK
    else:
        print("✗ Needs improvement - providing detailed feedback")
        return FEEDBACK


# Create the workflow
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node(RAG_ANSWER, get_rag_answer)
workflow.add_node(EVALUATE, evaluate_answer)
workflow.add_node(FEEDBACK, generate_feedback)

# Set entry point to get RAG answer first (retrieves docs + generates correct answer)
workflow.set_entry_point(RAG_ANSWER)

# Add edges: RAG_ANSWER -> EVALUATE -> decide_feedback -> FEEDBACK -> END
workflow.add_edge(RAG_ANSWER, EVALUATE)

workflow.add_conditional_edges(
    EVALUATE,
    decide_feedback,
    {
        FEEDBACK: FEEDBACK,
    }
)

workflow.add_edge(FEEDBACK, END)

# Compile the graph
evaluation_graph = workflow.compile()
