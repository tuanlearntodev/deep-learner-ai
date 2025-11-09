from typing import Dict, Any
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_core.documents import Document
from app.graph.rag_graph.state import GraphState

load_dotenv()

web_search_tool = TavilySearch(max_results=3)


def web_search(state: GraphState) -> Dict[str, Any]:
    print("--Web Search---")
    question = state["question"]
    documents = state["documents"]
    
    result = web_search_tool.invoke({"query": question})
    joined_res = "\n".join(
      [res["content"] for res in result["results"]]
    )
    search_res = Document(page_content=joined_res)
    if documents is not None:
        documents.append(search_res)
    else:
        documents = [search_res]
    return {"documents": documents, "question": question}
