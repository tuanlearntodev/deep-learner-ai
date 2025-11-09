from typing import TypedDict, List


class GraphState(TypedDict):
    question: str  # The question asked by AI (from previous message)
    user_answer: str  # User's answer to evaluate
    correct_answer: str  # Generated from RAG pipeline
    evaluation: str
    score: float
    feedback: str
    workspace_id: str
    subject: str
    documents: List[str]  # Retrieved documents from RAG
    web_search: bool  # Enable web search if needed
    crag: bool  # Enable CRAG for document checking
