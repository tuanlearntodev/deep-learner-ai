import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document as LangchainDocument
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.model.document import Document
from app.settings import settings
from dotenv import load_dotenv
load_dotenv()

STORAGE_DIR = Path("storage/documents")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


def get_vector_store(workspace_id: int):
    embeddings = get_embeddings()
    return PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
        namespace=f"workspace_{workspace_id}"
    )


def clean_metadata_for_pinecone(metadata: dict) -> dict:
    """
    Clean metadata to only include types supported by Pinecone:
    - strings, numbers, booleans, or lists of strings
    Remove complex nested objects, dicts, and lists of non-strings
    """
    cleaned = {}
    for key, value in metadata.items():
        # Skip None values
        if value is None:
            continue
        
        # Keep simple types: str, int, float, bool
        if isinstance(value, (str, int, float, bool)):
            cleaned[key] = value
        
        # Handle lists - only keep if all elements are strings
        elif isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                cleaned[key] = value
            # Convert list of simple types to list of strings
            elif all(isinstance(item, (str, int, float, bool)) for item in value):
                cleaned[key] = [str(item) for item in value]
        
        # Convert other types to string representation
        elif isinstance(value, (dict, tuple)):
            # Skip complex nested objects
            continue
        else:
            # Try to convert to string as fallback
            try:
                cleaned[key] = str(value)
            except:
                continue
    
    return cleaned


def load_and_chunk_document(
    file_path: str,
    workspace_id: int,
    document_id: int,
    file_name: str
) -> List[LangchainDocument]:
    """
    Load and chunk documents - parses all text into continuous content.
    Uses single mode to extract all text as one document.
    """
    loader = UnstructuredLoader(
        file_path=file_path,
        mode="single",  # Parse all text into one continuous content
        strategy="hi_res",  # Better extraction with GPU acceleration
        extract_images_in_pdf=False,
        infer_table_structure=True,
    )
    documents = loader.load()
    
    # Clean metadata and add custom fields
    for doc in documents:
        # Clean the existing metadata from unstructured
        cleaned_metadata = clean_metadata_for_pinecone(doc.metadata)
        
        # Add our required fields
        cleaned_metadata.update({
            "workspace_id": workspace_id,
            "document_id": document_id,
            "file_name": file_name,
            "source": file_name,
        })
        
        # Replace metadata with cleaned version
        doc.metadata = cleaned_metadata
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=500,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    
    chunked_documents = text_splitter.split_documents(documents)
    
    for i, doc in enumerate(chunked_documents):
        doc.metadata["chunk_index"] = i
    
    return chunked_documents


async def save_uploaded_file(
    file: UploadFile,
    workspace_id: int,
    document_id: int
) -> str:
    workspace_dir = STORAGE_DIR / f"workspace_{workspace_id}"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    file_path = workspace_dir / f"doc_{document_id}{file_extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)


async def process_and_store_document(
    file: UploadFile,
    workspace_id: int,
    document_id: int,
    db: Session
) -> tuple[int, str]:
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".pdf", ".doc", ".docx"]:
        raise ValueError(f"Unsupported file type: {file_extension}. Supported types: PDF, DOC, DOCX")
    
    file_path = None
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "PROCESSING"
            db.commit()
        
        file_path = await save_uploaded_file(file, workspace_id, document_id)
        
        chunked_documents = load_and_chunk_document(
            file_path=file_path,
            workspace_id=workspace_id,
            document_id=document_id,
            file_name=file.filename
        )
        
        vector_store = get_vector_store(workspace_id)
        vector_store.add_documents(chunked_documents)
        
        if document:
            document.status = "COMPLETED"
            db.commit()
        
        return len(chunked_documents), file_path
        
    except Exception as e:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "FAILED"
            db.commit()
        
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
        
        raise e


def create_document(
    db: Session,
    file_name: str,
    workspace_id: int
) -> Document:
    document = Document(
        file_name=file_name,
        workspace_id=workspace_id,
        status="PENDING"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def get_documents_by_workspace(
    db: Session,
    workspace_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[Document], int]:
    from app.model.workspace import Workspace
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    
    if not workspace:
        return [], 0
    
    total = db.query(Document).filter(
        Document.workspace_id == workspace_id
    ).count()
    
    documents = db.query(Document).filter(
        Document.workspace_id == workspace_id
    ).offset(skip).limit(limit).all()
    
    return documents, total


def get_document_by_id(
    db: Session,
    document_id: int,
    workspace_id: int,
    user_id: int
) -> Optional[Document]:
    from app.model.workspace import Workspace
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == user_id
    ).first()
    
    if not workspace:
        return None
    
    return db.query(Document).filter(
        Document.id == document_id,
        Document.workspace_id == workspace_id
    ).first()


def delete_document(
    db: Session,
    document_id: int,
    workspace_id: int,
    user_id: int
) -> bool:
    document = get_document_by_id(db, document_id, workspace_id, user_id)
    if not document:
        return False
    
    try:
        workspace_dir = STORAGE_DIR / f"workspace_{workspace_id}"
        file_extension = os.path.splitext(document.file_name)[1]
        file_path = workspace_dir / f"doc_{document_id}{file_extension}"
        if file_path.exists():
            os.unlink(file_path)
        
        vector_store = get_vector_store(workspace_id)
        vector_store.delete(filter={"document_id": document_id})
        
        db.delete(document)
        db.commit()
        
        return True
    except Exception as e:
        db.rollback()
        raise e
