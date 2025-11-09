from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    user = relationship("User", back_populates="workspaces", lazy="select")
    chat_messages = relationship("ChatMessage", back_populates="workspace", lazy="select", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="workspace", lazy="select", cascade="all, delete-orphan")
