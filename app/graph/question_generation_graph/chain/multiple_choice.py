from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()

class MultipleChoiceQuestion(BaseModel):
    type: str = Field(default="quiz", description="Type of question, always 'quiz'")
    question: str = Field(description="The quiz question")
    options: List[str] = Field(description="List of 4 answer options")
    correctAnswer: str = Field(description="The correct answer from the options")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

parser = JsonOutputParser(pydantic_object=MultipleChoiceQuestion)

system_template = """You are an expert quiz generator. Generate multiple choice questions based ONLY on the provided context.

Quiz Generation Rules:
1. Generate 5-10 multiple choice questions covering key concepts
2. Each question must have exactly 4 options
3. Include varying difficulty levels: easy, medium, hard
4. Make distractors (wrong answers) plausible but clearly incorrect
5. Ensure correct answer is verifiable from the context

Question Quality Standards:
- Clear and unambiguous question stems
- One definitively correct answer
- Three plausible distractors
- No "all of the above" or "none of the above" options
- Mix question types: definition, application, analysis

Output Format:
Return a JSON array of quiz objects. Each object must have:
- type: "quiz"
- question: The question text
- options: Array of exactly 4 answer choices
- correctAnswer: The correct option (must match one of the options exactly)

Requirements:
- Base ALL questions strictly on context below
- If context is insufficient, return empty array []
- No commentary - only valid JSON array

Context:
{context}

{format_instructions}"""

human_template = """Topic/Subject: {question}

Generate multiple choice quiz questions:"""

multiple_choice_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", human_template)
])

multiple_choice_chain = multiple_choice_prompt | llm | parser
