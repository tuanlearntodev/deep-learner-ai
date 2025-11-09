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
    model="gemini-2.5-flash-lite", 
    temperature=0
)

structured_llm_router = llm.with_structured_output(RouteQuery)

system = """You are routing queries for a workspace focused on: {subject}

Route to best data source:
- vector_store: Questions about uploaded documents/course materials related to {subject}
- web_search: Current events, recent information about {subject}, or when documents lack info"""

human = "{question}"

route_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])

question_router = route_prompt | structured_llm_router
