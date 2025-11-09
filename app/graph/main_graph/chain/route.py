from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


class Router(BaseModel):
    node: Literal["rag_node", "chat_node", "question_generation_node", "evaluation_node"] = Field(
        description="Route to appropriate node based on query type"
    )

ROUTER_SYSTEM_PROMPT = """You are a query router for a learning workspace focused on: {subject}

Route queries:
- evaluation_node: User provides an answer/explanation and wants evaluation OR user explicitly says "evaluate"
  Patterns:
  * User provides explanation/answer then says "evaluate": "A higher pleasure is... -> evaluate"
  * Direct evaluation request: "evaluate this", "check this", "is this correct"
  * User admits uncertainty: "I don't know", "I'm not sure", "Maybe it's...", "I think it's..."
  * Requests explanation of their answer: "can you explain", "is this correct", "am I right"
  * Asks for feedback: "how did I do", "check my answer", "evaluate my response"
  * Provides answer then asks: "is that right?", "correct?", "good answer?"
  * Format: JSON with "question", "user_answer", and "correct_answer" fields
  Keywords: "evaluate", "I don't know", "I'm not sure", "is this correct", "am I right", "can you explain", "grade my answer", "check my answer", "how did I do", "->", "→"
  
- question_generation_node: Requests to generate questions, create quiz, test, or study materials about {subject}
  Keywords: "generate questions", "quiz me", "test me", "create questions", "ask me about"
  
- rag_node: Questions seeking information, answers, or explanations from documents about {subject} (when NOT answering or being evaluated)
  Keywords: "what is", "explain", "how does", "tell me about", "define", "describe"
  
- chat_node: Greetings, casual conversation, or general chat
  Keywords: "hello", "hi", "thanks", "help"

IMPORTANT: 
1. If user writes explanation/answer followed by "evaluate" or "->", route to evaluation_node
2. If user shows uncertainty ("I don't know", "not sure") or asks if their answer is correct, route to evaluation_node

Priority: evaluation_node > question_generation_node > rag_node > chat_node"""

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
