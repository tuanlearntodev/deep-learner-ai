from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.graph.rag_graph.state import GraphState
from typing import Dict, Any
from app.graph.rag_graph.chain.document_checker import document_checker, CheckDocuments


def document_check(state: GraphState) -> Dict[str, Any]:
    print("--Grade Document---")
    question = state["question"]
    documents = state["documents"]
    filtered_doc = []
    
    # Preserve the original web_search setting from user input
    # Only set to True if we need web search due to irrelevant docs
    original_web_search = state.get("web_search", False)
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
            print("✗ Document not relevant to the question. May trigger web search.")
            needs_web_search = True
            continue
    
    # Enable web search if either:
    # 1. User explicitly enabled it, OR
    # 2. Documents are not relevant
    web_search = original_web_search or needs_web_search
    
    print(f"🔍 Web search status: {web_search} (original: {original_web_search}, needs: {needs_web_search})")

    return {"documents": filtered_doc, "question": question, "web_search": web_search}
