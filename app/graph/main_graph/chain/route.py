from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


class Router(BaseModel):
    node: Literal["rag_node", "chat_node", "question_generation_node"] = Field(
        description="Route to appropriate node based on query type"
    )

ROUTER_SYSTEM_PROMPT = """You are a query router for a learning workspace focused on: {subject}

Route queries:
- question_generation_node: Requests to generate questions, create quiz, test, or study materials about {subject}
  Keywords: "generate questions", "quiz me", "test me", "create questions", "ask me about"
- rag_node: Questions seeking information, answers, or explanations from documents about {subject}
  Keywords: "what is", "explain", "how does", "tell me about"
- chat_node: Greetings, casual conversation, or general chat
  Keywords: "hello", "hi", "thanks", "help"

Priority: question_generation_node > rag_node > chat_node"""

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
