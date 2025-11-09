from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
load_dotenv()

llm = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  temperature=0
)

class CheckHallucination(BaseModel):

    binary_score: bool = Field(description="Is the answer grounded in the documents? 'yes' or 'no'")

structured_llm_grader = llm.with_structured_output(CheckHallucination)

system = """Evaluate if the generated questions are grounded in the source documents.

Grade 'yes' if: All questions can be answered using information from the documents.
Grade 'no' if: Any question asks about information not present in the documents or contains hallucinations.

Rules:
1. Be strict - any unverifiable question = 'no'
2. Questions should be answerable from document content
3. Generic questions must relate to document topics"""

human = """Topic: {question}

Documents: {documents}

Generated Questions: {generation}

Are all questions fully based on the documents? Grade 'yes' or 'no'."""

hallucination_checker_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", human),
    ]
)


hallucination_checker = hallucination_checker_prompt | structured_llm_grader
