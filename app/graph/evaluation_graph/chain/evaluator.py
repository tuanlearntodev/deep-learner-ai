from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()


class EvaluateAnswer(BaseModel):
    score: float = Field(description="Score from 0.0 to 1.0 representing answer quality")
    correctness: str = Field(description="'correct', 'partially_correct', or 'incorrect'")
    explanation: str = Field(description="Brief explanation of the evaluation")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

structured_llm_evaluator = llm.with_structured_output(EvaluateAnswer)

system = """You are an expert evaluator assessing student answers to open-ended questions.

Your task:
1. Compare the user's answer to the correct answer
2. Use the provided course materials/documents as the authoritative source
3. Evaluate based on:
   - Accuracy of key concepts from the course materials
   - Completeness of the answer
   - Understanding demonstrated
   - Alignment with information in the documents
4. Assign a score from 0.0 to 1.0:
   - 1.0: Perfect answer, all key points from materials covered correctly
   - 0.7-0.9: Good answer, most key points covered with minor issues
   - 0.4-0.6: Partially correct, some key points but significant gaps
   - 0.1-0.3: Mostly incorrect, major misunderstandings
   - 0.0: Completely wrong or off-topic
5. Classify as: 'correct' (score >= 0.7), 'partially_correct' (0.4-0.69), or 'incorrect' (< 0.4)
6. Provide a BRIEF explanation (30-50 words) that is concise and focused

IMPORTANT: Keep your explanation SHORT - between 30-50 words only. Be direct and specific.

Be fair but thorough. Accept different phrasings if concepts are correct.
Reference the course materials when relevant."""

human = """Question: {question}

Correct Answer: {correct_answer}

User's Answer: {user_answer}

Course Materials/Context:
{context}

Evaluate the user's answer using the course materials as reference. Provide score, correctness classification, and explanation."""

evaluation_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", human)
])

answer_evaluator = evaluation_prompt | structured_llm_evaluator
