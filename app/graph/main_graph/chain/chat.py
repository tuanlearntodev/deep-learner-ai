from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


# System prompt for conversation
CHAT_SYSTEM_PROMPT = """You are a helpful AI learning assistant. 
Answer questions naturally based on the conversation history.
Be concise, friendly, and helpful."""

# Create prompt with message history
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", CHAT_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# Create the chat chain
chat_chain = chat_prompt | llm
