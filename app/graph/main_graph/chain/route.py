from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


class Router(BaseModel):
    node: Literal["rag_node", "chat_node"] = Field(
        description="Route to 'rag_node' for questions about documents/specific information, or 'chat_node' for general conversation."
    )

ROUTER_SYSTEM_PROMPT = """You are a query router for a learning workspace focused on: {subject}

Route queries:
- rag_node: Questions about documents, information, or facts related to {subject}
- chat_node: Greetings, casual chat, or general conversation related to {subject}"""

router_prompt = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    ("human", "{question}")
])

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

structured_llm_router = llm.with_structured_output(Router)

routing_chain = router_prompt | structured_llm_router
