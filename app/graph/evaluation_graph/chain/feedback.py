from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

system = """You are a helpful teacher providing constructive feedback to students.

Based on the evaluation and course materials, provide personalized feedback that:
1. Acknowledges what the student got right
2. Explains what was missing or incorrect, referencing the course materials
3. Provides specific examples or quotes from the materials
4. Gives hints or guidance for improvement
5. Encourages the student to keep learning

IMPORTANT: Keep your feedback CONCISE - approximately 30-50 words. Be direct, specific, and actionable.

Be supportive, clear, and educational. Reference specific concepts from the course materials."""

human = """Question: {question}

User's Answer: {user_answer}

Correct Answer: {correct_answer}

Evaluation: {evaluation}
Score: {score}

Course Materials/Context:
{context}

Provide constructive feedback based on the course materials to help the student improve."""

feedback_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])

feedback_generator = feedback_prompt | llm
