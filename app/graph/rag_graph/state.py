from typing import List, TypedDict


class GraphState(TypedDict):
    question: str
    generation: str
    web_search: bool
    crag: bool
    documents: List[str]
    answer_found: bool
    subject: str
    workspace_id: str
