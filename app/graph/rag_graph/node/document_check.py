from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.graph.rag_graph.state import GraphState
from typing import Dict, Any
from app.graph.rag_graph.chain.document_checker import document_checker, CheckDocuments


def document_check(state: GraphState) -> Dict[str, Any]:
    print("--Grade Document---")
    question = state["question"]
    documents= state["documents"]
    filtered_doc=[]
    web_search = False
    for doc in documents:
        score: CheckDocuments = document_checker.invoke(
            {"question": question, "document": doc}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            print("Document relevant to the question.")
            filtered_doc.append(doc)
        else:
            print("Document not relevant to the question. Triggering web search.")
            web_search = True
            continue

    return {"documents": filtered_doc, "question": question, "web_search": web_search}
