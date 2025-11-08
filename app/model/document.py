from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):

    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    status = Column(String(50), default="PENDING")
    
    # This creates a link: a Document has many Chunks
    workspace = relationship("Workspace", back_populates="documents")