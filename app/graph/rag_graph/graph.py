from dotenv import load_dotenv
from langgraph.graph import END,StateGraph
from app.graph.rag_graph.chain import hallucination_checker,answer_checker, question_router, RouteQuery
from app.graph.rag_graph.node import retrieve,document_check,web_search,generate_answer
from app.graph.rag_graph.state import GraphState
load_dotenv()

RETRIEVE = "retrieve"
GENERATE_ANSWER = "generate_answer"
DOCUMENT_CHECK = "document_check"
WEB_SEARCH = "web_search"


def decide_web_search(state: GraphState) -> str:
    print("--Decide Web Search---")
    if state["web_search"]:
        return WEB_SEARCH
    else:
        return GENERATE_ANSWER

def route_after_retrieve(state: GraphState) -> str:
    """Route after retrieval based on CRAG flag"""
    if state.get("crag", True):
        return DOCUMENT_CHECK
    else:
        return GENERATE_ANSWER

def check_hallucination_and_answer(state: GraphState) -> str:
    print("--Check Hallucination---")
    question = state["question"]
    generation = state["generation"]
    documents = state["documents"]
    
    if not state.get("answer_found", True):
        print("ℹ Answer not found in source material")
        return "not_found"
    
    score = hallucination_checker.invoke(
        {"question": question, "generation": generation, "documents": documents}
    )
    if score.binary_score:
        print("✓ Answer is grounded in documents")
        print("--Check Answer Relevance---")
        answer_score = answer_checker.invoke(
            {"question": question, "generation": generation}
        )
        if answer_score.binary_score.lower() == "yes":
            print("✓ Answer addresses the question")
            return "relevant"
        else:
            print("✗ Answer does not address the question")
            return "not_relevant"
    else:
        print("✗ Answer contains hallucinations")
        return "not_grounded"


def route_question(state: GraphState) -> str:
    print("--Router---")
    
    if not state.get("crag", True):
        print("--CRAG disabled, routing directly to Vector Store---")
        return RETRIEVE
    
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("--Routing to Web Search---")
        return WEB_SEARCH
    else:
        print("--Routing to Vector Store---")
        return RETRIEVE
      
workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(WEB_SEARCH, web_search)
workflow.add_node(GENERATE_ANSWER, generate_answer)
workflow.add_node(DOCUMENT_CHECK, document_check)

workflow.set_conditional_entry_point(
  route_question,
  {
      RETRIEVE: RETRIEVE,
      WEB_SEARCH: WEB_SEARCH,
  }
)
workflow.add_conditional_edges(
  RETRIEVE,
  route_after_retrieve,
  {
      DOCUMENT_CHECK: DOCUMENT_CHECK,
      GENERATE_ANSWER: GENERATE_ANSWER,
  }
)
workflow.add_conditional_edges(
  DOCUMENT_CHECK,
  decide_web_search,
  {
      WEB_SEARCH: WEB_SEARCH,
      GENERATE_ANSWER: GENERATE_ANSWER,
  }
)

workflow.add_edge(WEB_SEARCH, GENERATE_ANSWER)

workflow.add_conditional_edges(
  GENERATE_ANSWER,
  check_hallucination_and_answer,
  {
      "relevant": END,
      "not_relevant": GENERATE_ANSWER,
      "not_grounded": WEB_SEARCH,
      "not_found": END,
  }
)

rag_graph = workflow.compile()

rag_graph.get_graph().draw_mermaid_png(output_file_path="rag_graph_workflow.png")