from typing import Dict, Any
from app.graph.question_generation_graph.state import QuestionGraphState
from app.graph.question_generation_graph.chain.document_checker import document_checker, CheckDocuments


def document_check(state: QuestionGraphState) -> Dict[str, Any]:
    print("--Grade Document---")
    question = state["question"]
    documents = state["documents"]
    filtered_doc = []
    
    # Respect the user's web_search setting
    # Only enable web search if user explicitly enabled it
    web_search_enabled = state.get("web_search", False)
    needs_web_search = False
    
    for doc in documents:
        score: CheckDocuments = document_checker.invoke(
            {"question": question, "document": doc}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            print("✓ Document relevant to the question.")
            filtered_doc.append(doc)
        else:
            print("✗ Document not relevant to the question.")
            needs_web_search = True
            continue
    
    # Only enable web search if:
    # 1. User explicitly enabled it AND
    # 2. Documents are not relevant
    # If web_search is disabled, we won't trigger it even if docs are irrelevant
    web_search = web_search_enabled and needs_web_search
    
    if needs_web_search and not web_search_enabled:
        print("⚠️ Documents not relevant but web_search is disabled by user")
    
    print(f"🔍 Web search status: {web_search} (user enabled: {web_search_enabled}, needs: {needs_web_search})")

    return {"documents": filtered_doc, "question": question, "web_search": web_search}
