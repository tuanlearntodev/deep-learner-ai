from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
import os
from app.graph.rag_graph.state import GraphState

load_dotenv()

# Create retriever
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
index_name = os.getenv("PINECONE_INDEX_NAME")

retriever = PineconeVectorStore.from_existing_index(
    embedding=embeddings,
    index_name=index_name
).as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

def retrieve(state: GraphState) -> Dict[str, Any]:
    # Retrieve documents from Pinecone
    print("--Retrieve---")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}
