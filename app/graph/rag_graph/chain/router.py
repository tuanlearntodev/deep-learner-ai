from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

class RouteQuery(BaseModel):
    datasource: Literal["vector_store", "web_search"] = Field(
        description="Given the question, decide whether to route to 'vector_store' or 'web_search' to find relevant information."
)
    
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0
)

structured_llm_router = llm.with_structured_output(RouteQuery)

system = """Route questions to the best data source.

'vector_store': Philosophy questions (concepts, theories, philosophers like Mill/Kant/Plato, ethics, metaphysics, epistemology, logic, political philosophy, moral reasoning, utilitarianism, deontology, virtue ethics, philosophy of mind/religion/science/language, philosophical texts)

'web_search': Non-philosophy questions (current events, news, sports, science, technology, math, history, geography, how-to, general knowledge)

Rules:
1. Any philosophical topic/concept/philosopher → 'vector_store'
2. Clearly non-philosophy → 'web_search'
3. Vector store = philosophy course materials
4. When unsure → 'vector_store'"""

human = """Question: {question}

Philosophy question? Route to 'vector_store'. Otherwise 'web_search'."""

route_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])

question_router = route_prompt | structured_llm_router