from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

class CheckAnswer(BaseModel):

    binary_score: str = Field(description="Does the answer address the question 'yes' or 'no'")
    
    
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
structured_llm_grader = llm.with_structured_output(CheckAnswer)

system = """Evaluate if the answer addresses the question.

Grade 'yes': Answer attempts to address the question (directly, partially, or with relevant info).
Grade 'no': Answer completely ignores question, off-topic, or unhelpful.

Be lenient - partial/imperfect answers that are relevant = 'yes'."""

human = """Question: {question}

Answer: {generation}

Does the answer address the question? Grade 'yes' or 'no'."""

answer_check_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])

answer_checker = answer_check_prompt | structured_llm_grader