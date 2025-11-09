from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.schema.document import (
    DocumentResponse,
    DocumentList,
    DocumentUploadResponse,
)
from app.services.dependencies import get_db, get_current_active_user
from app.services.workspace_service import check_workspace_exists
from app.services.document_service import (
    create_document,
    get_documents_by_workspace,
    get_document_by_id,
    delete_document,
    process_and_store_document,
)
from app.model.user import User

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a PDF, DOC, or DOCX file. The document will be stored, chunked, embedded, and ingested to Pinecone."
)
async def upload_document(
    workspace_id: int,
    file: UploadFile = File(..., description="Document file (PDF, DOC, or DOCX)"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Session = Depends(get_db),
):
    if not check_workspace_exists(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["pdf", "doc", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC, and DOCX files are supported"
        )
    
    try:
        document = create_document(
            db=db,
            file_name=file.filename,
            workspace_id=workspace_id
        )
        
        chunks_created, file_path = await process_and_store_document(
            file=file,
            workspace_id=workspace_id,
            document_id=document.id,
            db=db
        )
        
        return DocumentUploadResponse(
            document=document,
            message=f"Document uploaded, chunked, embedded, and ingested to Pinecone successfully",
            chunks_created=chunks_created,
            file_path=file_path
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get(
    "/",
    response_model=DocumentList,
    summary="List documents",
    description="Get all documents in a workspace."
)
async def list_documents(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
):
    if not check_workspace_exists(db, workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace with ID {workspace_id} not found"
        )
    documents, total = get_documents_by_workspace(
        db=db,
        workspace_id=workspace_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return DocumentList(
        documents=documents,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
    description="Get a specific document by its ID."
)
async def get_document(
    workspace_id: int,
    document_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    document = get_document_by_id(
        db=db,
        document_id=document_id,
        workspace_id=workspace_id,
        user_id=current_user.id
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found in workspace {workspace_id}"
        )
    
    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document and its embeddings from Pinecone."
)
async def delete_document_endpoint(
    workspace_id: int,
    document_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    try:
        success = delete_document(
            db=db,
            document_id=document_id,
            workspace_id=workspace_id,
            user_id=current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found in workspace {workspace_id}"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )
