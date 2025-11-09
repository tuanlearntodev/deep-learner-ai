import operator
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

    workspace_id: str
    
    web_search: bool
    
    crag: bool
