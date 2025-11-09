from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()


class Flashcard(BaseModel):
    type: str = Field(default="flashcard", description="Type of card, always 'flashcard'")
    front: str = Field(description="The question or prompt on the front of the card")
    back: str = Field(description="The answer or explanation on the back of the card")
    category: str = Field(description="Category or topic of the flashcard (e.g., 'definition', 'concept', 'formula', 'example')")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

parser = JsonOutputParser(pydantic_object=Flashcard)

system_template = """You are an expert flashcard creator. Generate educational flashcards based ONLY on the provided context.

Flashcard Generation Rules:
1. Generate exactly {num_questions} flashcards covering key concepts
2. Each flashcard should have a clear front (question/prompt) and back (answer/explanation)
3. Include varying difficulty levels: easy, medium, hard
4. Make cards concise but informative
5. Focus on important facts, definitions, concepts, and relationships

Flashcard Types to Include:
- Definition Cards: "What is X?" → "X is..."
- Concept Cards: "Explain Y" → "Y is a concept that..."
- Formula Cards: "Formula for Z?" → "Z = ..."
- Example Cards: "Give an example of..." → "An example is..."
- Comparison Cards: "Difference between A and B?" → "A is..., while B is..."

Output Format:
Return a JSON array of flashcard objects. Each object must have:
- type: "flashcard"
- front: The question or prompt (concise, 1-2 sentences max)
- back: The answer or explanation (clear, 2-4 sentences)
- category: Classification of the card (definition/concept/formula/example/comparison)

Requirements:
- Generate EXACTLY {num_questions} flashcards, no more, no less
- Base ALL flashcards strictly on context below
- Keep front concise and engaging
- Make back informative but not too long
- If context is insufficient, return empty array []
- No commentary - only valid JSON array

Context:
{context}

{format_instructions}"""

human_template = """Topic/Subject: {question}

Generate exactly {num_questions} flashcards:"""

flashcard_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", human_template)
])

flashcard_chain = flashcard_prompt | llm | parser
