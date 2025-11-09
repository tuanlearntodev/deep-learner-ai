from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


class Router(BaseModel):
    """Router decision for query routing."""
    node: Literal["rag_node", "chat_node"] = Field(
        description="Route to 'rag_node' for questions about documents/specific information, or 'chat_node' for general conversation."
    )


# System prompt for the router
ROUTER_SYSTEM_PROMPT = """Route queries: 
- rag_node: questions about documents/information/facts
- chat_node: greetings/casual chat"""

# Create the prompt template
router_prompt = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    ("human", "{question}")
])

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

# Create the structured output chain
structured_llm_router = llm.with_structured_output(Router)

# Create the complete routing chain
routing_chain = router_prompt | structured_llm_router
