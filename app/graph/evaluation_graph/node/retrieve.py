from typing import Any, Dict
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from app.graph.evaluation_graph.state import GraphState
from app.settings import settings


def get_workspace_retriever(workspace_id: str):
    """
    Create a retriever for a specific workspace using Pinecone namespace.
    Each workspace has its own isolated document collection.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    vector_store = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
        namespace=f"workspace_{workspace_id}"
    )
    
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )


def retrieve_for_evaluation(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve relevant documents for evaluation context.
    Uses the question and correct answer to find relevant course materials.
    """
    print("---EVALUATION: Retrieve Documents---")
    question = state["question"]
    correct_answer = state.get("correct_answer", "")
    workspace_id = state.get("workspace_id")
    
    if not workspace_id:
        print("⚠️ Warning: No workspace_id in state, skipping retrieval")
        return {"documents": []}
    
    print(f"📂 Retrieving from workspace: {workspace_id}")
    print(f"📝 Query: {question}")
    
    # Get workspace-specific retriever
    retriever = get_workspace_retriever(workspace_id)
    
    # Combine question and correct answer for better retrieval
    query = f"{question} {correct_answer}"
    
    # Retrieve documents
    documents = retriever.invoke(query)
    
    print(f"✅ Retrieved {len(documents)} documents for evaluation context")
    
    # Extract page content from documents
    document_texts = [doc.page_content for doc in documents]
    
    return {"documents": document_texts}
