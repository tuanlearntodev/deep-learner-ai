from typing import Any, Dict
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from app.graph.rag_graph.state import GraphState
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

def retrieve(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve relevant documents from the workspace-specific vector store.
    Uses the workspace_id from state to ensure documents are fetched from the correct workspace.
    """
    print("--Retrieve---")
    question = state["question"]
    workspace_id = state.get("workspace_id")
    
    if not workspace_id:
        print("⚠️ Warning: No workspace_id in state, retrieval may fail")
        return {"documents": [], "question": question}
    
    print(f"📂 Retrieving from workspace: {workspace_id}")
    
    # Get workspace-specific retriever
    retriever = get_workspace_retriever(workspace_id)
    
    # Retrieve documents
    documents = retriever.invoke(question)
    
    print(f"✅ Retrieved {len(documents)} documents")
    
    return {"documents": documents, "question": question}
