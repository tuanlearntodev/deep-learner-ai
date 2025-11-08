from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., 'user' or 'assistant'
    content = Column(Text, nullable=False)

    workspace = relationship("Workspace", back_populates="chat_messages")