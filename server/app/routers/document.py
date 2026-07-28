from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.document_schema import DocumentListResponse
from app.services.document_service import DocumentService
from fastapi import status

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=DocumentListResponse,
)
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    documents = service.get_documents(current_user)

    return DocumentListResponse(
        documents=documents,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    service.delete_document(
        document_id=document_id,
        current_user=current_user,
    )
