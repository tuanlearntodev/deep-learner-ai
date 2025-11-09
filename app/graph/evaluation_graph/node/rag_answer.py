from typing import Any, Dict
from app.graph.evaluation_graph.state import GraphState
from app.graph.rag_graph import rag_graph
from app.graph.rag_graph.state import GraphState as RagState


def get_rag_answer(state: GraphState) -> Dict[str, Any]:
    """
    Use RAG graph to retrieve documents and generate the correct answer.
    This provides both the reference answer and supporting documents.
    Follows main graph settings for web_search and crag.
    """
    print("---EVALUATION: Get RAG Answer---")
    
    question = state["question"]
    workspace_id = state.get("workspace_id")
    subject = state.get("subject", "general learning")
    web_search = state.get("web_search", False)
    crag = state.get("crag", False)  # Use False as default to match main graph
    
    print(f"📝 Question: {question}")
    print(f"📂 Workspace: {workspace_id}")
    print(f"🌐 Web search enabled: {web_search}")
    print(f"🔍 CRAG enabled: {crag}")
    
    # Prepare RAG graph state with main graph settings
    rag_state: RagState = {
        "question": question,
        "generation": "",
        "web_search": web_search,  # Use main graph setting
        "crag": crag,  # Use main graph setting
        "documents": [],
        "answer_found": True,
        "subject": subject,
        "workspace_id": workspace_id
    }
    
    # Invoke RAG graph to get answer and documents
    result = rag_graph.invoke(rag_state)
    
    # Extract results
    correct_answer = result.get("generation", "")
    documents = result.get("documents", [])
    
    print(f"✅ Generated correct answer: {correct_answer[:100]}...")
    print(f"📚 Retrieved {len(documents)} documents")
    
    # Extract text content from documents
    if documents and len(documents) > 0:
        if hasattr(documents[0], 'page_content'):
            document_texts = [doc.page_content for doc in documents]
        else:
            document_texts = documents
    else:
        document_texts = []
    
    return {
        "correct_answer": correct_answer,
        "documents": document_texts
    }
