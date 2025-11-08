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

system = """Evaluate if the generated answer is grounded in the source documents.

Grade 'yes' if: All claims can be traced to the documents (direct quotes, paraphrasing, or reasonable inference).
Grade 'no' if: Any part contains unsupported information, hallucinations, or contradicts the documents.

Rules:
1. Be strict - any unverifiable claim = 'no'
2. Reasonable inference OK, speculation not OK
3. Generic knowledge must be document-supported"""

human = """Question: {question}

Documents: {documents}

Answer: {generation}

Is the answer fully supported by the documents? Grade 'yes' or 'no'."""

hallucination_checker_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", human),
    ]
)


hallucination_checker = hallucination_checker_prompt | structured_llm_grader