from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7  # Higher temperature for more creative question generation
)

system_template = """You are an expert question generator. Generate educational questions based ONLY on the provided context.

Question Generation Rules:
1. Generate 5 diverse questions covering the main concepts
2. Mix question types: factual, conceptual, analytical, and application-based
3. Questions must be answerable using ONLY the provided context
4. Include varying difficulty levels: easy, medium, hard
5. Format as numbered list

Question Types to Include:
- Factual: "What is...?", "Define...", "List..."
- Conceptual: "Explain...", "Describe...", "How does..."
- Analytical: "Compare...", "Why...", "What is the relationship..."
- Application: "How would you apply...", "What would happen if..."

Requirements:
- Base questions strictly on context below
- If context is insufficient, state: "Not enough context to generate meaningful questions."
- No commentary—only the numbered question list
- Create number of questions based on the user prompt first, if not give the default: 5

Context:
{context}"""

human_template = """Topic/Subject: {question}

Generate questions:"""

question_generation_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", human_template)
])

generation_chain = question_generation_prompt | llm | StrOutputParser()
