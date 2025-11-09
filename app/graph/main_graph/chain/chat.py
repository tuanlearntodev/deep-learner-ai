from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


CHAT_SYSTEM_PROMPT = """You are a helpful AI learning assistant for a workspace focused on: {subject}

Answer questions naturally based on the conversation history.
Be concise, friendly, and helpful.

IMPORTANT: Keep all responses relevant to {subject}. If the user asks about unrelated topics, politely guide them back to the subject."""

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", CHAT_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

chat_chain = chat_prompt | llm
