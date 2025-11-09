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

system = """Evaluate if the generated questions are relevant to the topic.

Grade 'yes': Questions are directly related to the topic/subject matter.
Grade 'no': Questions are completely off-topic or unhelpful.

Be lenient - questions that explore the topic from different angles = 'yes'."""

human = """Topic: {question}

Generated Questions: {generation}

Are the questions relevant to the topic? Grade 'yes' or 'no'."""

answer_check_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])

answer_checker = answer_check_prompt | structured_llm_grader
