from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

class RouteGeneration(BaseModel):
    generation_type: Literal["open_ended", "multiple_choice"] = Field(
        description="Question type: 'open_ended' for general questions, 'multiple_choice' for quiz/test"
    )
    
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
structured_llm_router = llm.with_structured_output(RouteGeneration)

system = """Route question requests to the appropriate generation type:

'multiple_choice' → quiz, test, MCQ, exam, assessment
'open_ended' → general questions, discussion, study questions (default)"""

human = "Request: {question}\nSubject: {subject}\nType:"

generation_router_prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
generation_router = generation_router_prompt | structured_llm_router
