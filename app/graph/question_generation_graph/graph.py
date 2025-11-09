from dotenv import load_dotenv
from langgraph.graph import END,StateGraph
from app.graph.question_generation_graph.chain import (
    hallucination_checker,
    answer_checker, 
    question_router, 
    RouteQuery,
    generation_router,
    RouteGeneration
)
from app.graph.question_generation_graph.node import (
    retrieve,
    document_check,
    web_search,
    generate_questions,
    generate_multiple_choice,
    generate_flashcards
)
from app.graph.question_generation_graph.state import QuestionGraphState
load_dotenv()

RETRIEVE = "retrieve"
GENERATE_QUESTIONS = "generate_questions"
GENERATE_MULTIPLE_CHOICE = "generate_multiple_choice"
GENERATE_FLASHCARDS = "generate_flashcards"
DOCUMENT_CHECK = "document_check"
WEB_SEARCH = "web_search"


def decide_web_search(state: QuestionGraphState) -> str:
    print("--Decide Web Search---")
    if state["web_search"]:
        return WEB_SEARCH
    else:
        # Route to appropriate generation type
        return route_generation_type(state)

def route_after_retrieve(state: QuestionGraphState) -> str:
    if state.get("crag", True):
        return DOCUMENT_CHECK
    else:
        # Route to appropriate generation type
        return route_generation_type(state)

def route_generation_type(state: QuestionGraphState) -> str:
    print("--Generation Type Router---")
    question = state["question"]
    subject = state.get("subject", "general learning")
    
    route: RouteGeneration = generation_router.invoke({
        "question": question, 
        "subject": subject
    })
    
    if route.generation_type == "flashcard":
        print("--Routing to Flashcard Generation---")
        return GENERATE_FLASHCARDS
    elif route.generation_type == "multiple_choice":
        print("--Routing to Multiple Choice Generation---")
        return GENERATE_MULTIPLE_CHOICE
    else:
        print("--Routing to Open-Ended Question Generation---")
        return GENERATE_QUESTIONS

def check_hallucination_and_answer(state: QuestionGraphState) -> str:
    print("--Check Question Quality---")
    question = state["question"]
    generation = state["generation"]
    documents = state["documents"]
    
    if not state.get("answer_found", True):
        print("ℹ Not enough context to generate questions")
        return "not_found"
    
    score = hallucination_checker.invoke(
        {"question": question, "generation": generation, "documents": documents}
    )
    if score.binary_score:
        print("✓ Questions are grounded in documents")
        print("--Check Question Relevance---")
        answer_score = answer_checker.invoke(
            {"question": question, "generation": generation}
        )
        if answer_score.binary_score.lower() == "yes":
            print("✓ Questions are relevant to the topic")
            return "relevant"
        else:
            print("✗ Questions are not relevant to the topic")
            return "not_relevant"
    else:
        print("✗ Questions contain hallucinations")
        return "not_grounded"


def route_question(state: QuestionGraphState) -> str:
    print("--Router---")
    
    if not state.get("crag", True):
        print("--CRAG disabled, routing directly to Vector Store---")
        return RETRIEVE
    
    question = state["question"]
    subject = state.get("subject", "general learning")
    source: RouteQuery = question_router.invoke({"question": question, "subject": subject})
    if source.datasource == "web_search":
        print("--Routing to Web Search---")
        return WEB_SEARCH
    else:
        print("--Routing to Vector Store---")
        return RETRIEVE
      
workflow = StateGraph(QuestionGraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(WEB_SEARCH, web_search)
workflow.add_node(GENERATE_QUESTIONS, generate_questions)
workflow.add_node(GENERATE_MULTIPLE_CHOICE, generate_multiple_choice)
workflow.add_node(GENERATE_FLASHCARDS, generate_flashcards)
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
      GENERATE_QUESTIONS: GENERATE_QUESTIONS,
      GENERATE_MULTIPLE_CHOICE: GENERATE_MULTIPLE_CHOICE,
      GENERATE_FLASHCARDS: GENERATE_FLASHCARDS,
  }
)
workflow.add_conditional_edges(
  DOCUMENT_CHECK,
  decide_web_search,
  {
      WEB_SEARCH: WEB_SEARCH,
      GENERATE_QUESTIONS: GENERATE_QUESTIONS,
      GENERATE_MULTIPLE_CHOICE: GENERATE_MULTIPLE_CHOICE,
      GENERATE_FLASHCARDS: GENERATE_FLASHCARDS,
  }
)

# Web search routes to generation type router
workflow.add_conditional_edges(
  WEB_SEARCH,
  route_generation_type,
  {
      GENERATE_QUESTIONS: GENERATE_QUESTIONS,
      GENERATE_MULTIPLE_CHOICE: GENERATE_MULTIPLE_CHOICE,
      GENERATE_FLASHCARDS: GENERATE_FLASHCARDS,
  }
)

workflow.add_conditional_edges(
  GENERATE_QUESTIONS,
  check_hallucination_and_answer,
  {
      "relevant": END,
      "not_relevant": GENERATE_QUESTIONS,
      "not_grounded": WEB_SEARCH,
      "not_found": END,
  }
)

workflow.add_conditional_edges(
  GENERATE_MULTIPLE_CHOICE,
  check_hallucination_and_answer,
  {
      "relevant": END,
      "not_relevant": GENERATE_MULTIPLE_CHOICE,
      "not_grounded": WEB_SEARCH,
      "not_found": END,
  }
)

workflow.add_conditional_edges(
  GENERATE_FLASHCARDS,
  check_hallucination_and_answer,
  {
      "relevant": END,
      "not_relevant": GENERATE_FLASHCARDS,
      "not_grounded": WEB_SEARCH,
      "not_found": END,
  }
)

question_generation_graph = workflow.compile()
