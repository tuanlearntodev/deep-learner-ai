from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

class CheckDocuments(BaseModel):

    binary_score: str = Field(description="Documents are relevant to the question: 'yes' or 'no'")
    

structured_llm_grader = llm.with_structured_output(CheckDocuments)

system = """Evaluate if the document can help generate questions about the topic.

Grade 'yes': Document contains relevant content, concepts, or information for question generation.
Grade 'no': Document completely off-topic or unhelpful for the topic.

Be lenient - any useful information = 'yes'."""
document_check_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n Topic/Subject: {question}"),
    ]
)

document_checker = document_check_prompt | structured_llm_grader
