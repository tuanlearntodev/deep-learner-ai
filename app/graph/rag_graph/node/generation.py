from langsmith import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Dict
from app.graph.rag_graph.state import GraphState
from app.graph.rag_graph.chain.generation import generation_chain


def generate_answer(state: GraphState) -> Dict[str, Any]:
    print("--Generate Answer---")
    question = state["question"]
    documents = state["documents"]

    generation = generation_chain.invoke({"question": question, "context": documents})
    
    # Check if answer indicates information not found
    answer_found = "information not available" not in generation.lower()
    
    return {"documents": documents, "question": question, "generation": generation, "answer_found": answer_found}
